"""
AI Profile Service - OpenAI Integration für Idealprofil-Generierung und Bewertung

Verwendet OpenAI GPT-4o-mini für:
1. Generierung eines idealen OCEAN-Profils basierend auf Hunde-Metadaten
2. Bewertung und Vergleich von 3 Profilen (Ist, Ideal, Fragebogen)
"""
import json
from typing import Optional, Dict
from openai import OpenAI, OpenAIError, APIConnectionError, APITimeoutError, RateLimitError
from src.settings import settings
from src.models import DogData


class AIProfileError(Exception):
    """Basis-Exception für AI-Service-Fehler"""
    pass


class AIProfileConnectionError(AIProfileError):
    """Exception bei Verbindungsproblemen zur API"""
    pass


class AIProfileConfigError(AIProfileError):
    """Exception bei Konfigurationsproblemen"""
    pass


class AIProfileService:
    """
    Service für OpenAI-basierte Profil-Generierung und -Bewertung
    
    Generiert IDEALE Persönlichkeitsprofile basierend auf Rasse, Alter, Geschlecht
    und Einsatzgebiet. Das Idealprofil repräsentiert die optimalen OCEAN-Werte,
    die ein Hund für eine spezifische Aufgabe haben sollte.
    
    Beispiel:
        service = AIProfileService()
        
        # IDEAL-Profil für Therapiehund generieren (optimale Werte für die Rolle)
        ideal = service.get_ideal_profile(
            breed="Golden Retriever",
            age_years=3,
            age_months=6,
            gender="Rüde",
            intended_use="Therapiehund",
            test_count=7
        )
        # → {'O': 10, 'C': 12, 'E': 8, 'A': 14, 'N': -10}
        #    (hohe Verträglichkeit, niedrige Nervosität für Therapiearbeit)
        
        # 3-Profil-Bewertung erstellen
        assessment = service.get_assessment(
            dog_data=dog_data,
            ist_profile={'O': 8, 'C': 10, 'E': 6, 'A': 12, 'N': -6},  # Tatsächliche Werte
            ideal_profile={'O': 10, 'C': 12, 'E': 8, 'A': 14, 'N': -10},  # Sollwerte
            owner_profile={'O': 9, 'C': 11, 'E': 7, 'A': 13, 'N': -8}  # Erwartungen
        )
        # → "Der Hund zeigt gute Eignung für Therapiearbeit..."
    """
    
    def __init__(self):
        """
        Initialisiert den AI Service
        
        Raises:
            AIProfileConfigError: Wenn OpenAI nicht konfiguriert ist
        """
        if not settings.is_openai_configured:
            raise AIProfileConfigError(
                "OpenAI API Key ist nicht konfiguriert. "
                "Bitte erstelle eine .env Datei mit OPENAI_API_KEY. "
                "Siehe .env.example für Details."
            )
        
        config = settings.get_openai_config()
        self.client = OpenAI(
            api_key=config['api_key'],
            timeout=config['timeout']
        )
        self.model = config['model']
        self.max_tokens = config['max_tokens']
    
    def get_ideal_profile(
        self,
        breed: str,
        age_years: int,
        age_months: int,
        gender: str,
        intended_use: str,
        test_count: int = 7
    ) -> Dict[str, int]:
        """
        Generiert ein ideales OCEAN-Profil für einen Hund basierend auf dessen
        Eigenschaften und dem vorgesehenen Einsatzgebiet.
        
        Das Profil repräsentiert die IDEALEN Persönlichkeitswerte, die ein Hund
        für die spezifische Aufgabe haben sollte - nicht die erwarteten IST-Werte.
        
        Args:
            breed: Rasse des Hundes (z.B. "Deutscher Schäferhund")
            age_years: Alter in Jahren
            age_months: Alter in Monaten (zusätzlich)
            gender: Geschlecht ("Rüde" oder "Hündin")
            intended_use: Einsatzgebiet (z.B. "Therapiehund", "Familienhund", "Rettungshund")
            test_count: Anzahl Tests pro Dimension (für Skalierung)
            
        Returns:
            Dict mit Keys 'O', 'C', 'E', 'A', 'N' und Integer-Werten im Bereich
            -test_count*2 bis +test_count*2 (z.B. -14 bis +14 bei 7 Tests)
            
        Raises:
            AIProfileConnectionError: Bei Verbindungsproblemen
            AIProfileError: Bei anderen API-Fehlern
        """
        max_value = test_count * 2
        age_total = age_years + (age_months / 12.0)
        
        prompt = f"""You are a working dog behavior specialist with expertise in canine personality assessment using the OCEAN model.

I need you to generate the OPTIMAL OCEAN personality profile for a dog that would ideally suit the following characteristics and role:

Dog Characteristics:
- Breed: {breed}
- Age: {age_years} years and {age_months} months (total: {age_total:.1f} years)
- Sex: {gender}
- Intended Use/Role: {intended_use}

OCEAN Dimensions (Big Five for Dogs):
- O (Openness): Curiosity, learning ability, adaptability to new situations
- C (Conscientiousness): Reliability, impulse control, focus, trainability
- E (Extraversion): Social behavior, energy level, contact-seeking behavior
- A (Agreeableness): Friendliness, cooperation, compatibility with others
- N (Neuroticism): Nervousness, anxiety, emotional stability (negative values = stable)

Your task: Generate the IDEAL personality values that a dog should have to excel in the specified role "{intended_use}".

Consider:
- Breed-specific tendencies and their suitability for the role
- Age-appropriate development and maturity requirements
- Gender-specific behavioral patterns
- Specific requirements of the intended use case (e.g., therapy dogs need high Agreeableness and low Neuroticism, working dogs need high Conscientiousness)

CRITICAL SCORING RULES - STRICTLY FOLLOW THESE:
1. **Valid Range**: ALL values MUST be integers between {-max_value} and {+max_value} (inclusive)
   - Minimum allowed: {-max_value}
   - Maximum allowed: {+max_value}
   - Example valid values: -13, -8, -3, 0, 5, 10, 13
   
2. **AVOID EXTREME VALUES**: Do NOT use the absolute limits ({-max_value} or {+max_value}) unless absolutely necessary
   - Prefer values in the moderate-to-high range: -12 to +12
   - Reserve extremes only for exceptional cases
   
3. **Realistic Distribution**: Use a balanced distribution
   - Most values should be between -10 and +10
   - Perfect dogs don't exist - include some moderate values
   - Consider that even ideal dogs have personality nuances

4. **Value Interpretation**:
   - Highly positive (8-12): Strong trait expression, essential for role
   - Moderate positive (3-7): Beneficial trait, helpful for role  
   - Neutral (−2 to +2): Trait not critical for role
   - Moderate negative (−7 to −3): Low expression preferred
   - Highly negative (−12 to −8): Very low expression essential (e.g., low anxiety for therapy work)

Response Format:
Return ONLY a valid JSON object with the five traits and their ideal scores. No explanations or additional text.

{{"O": <integer>, "C": <integer>, "E": <integer>, "A": <integer>, "N": <integer>}}

Example for {test_count} tests (range {-max_value} to {+max_value}):
{{"O": 7, "C": 11, "E": 5, "A": 9, "N": -8}}
(Note: Realistic values avoiding extremes)
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a working dog behavior specialist with expertise in canine personality assessment and the OCEAN model for dogs. Always follow scoring constraints strictly."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,  # Reduziert für fokussierte JSON-Antwort
                temperature=0.3,  # Niedriger für konsistentere, regelkonforme Ausgaben
                response_format={"type": "json_object"}
            )
            
            # Response parsen
            content = response.choices[0].message.content
            profile = json.loads(content)
            
            # Validierung
            required_keys = {'O', 'C', 'E', 'A', 'N'}
            if not all(key in profile for key in required_keys):
                raise AIProfileError(f"Ungültige Response: Fehlende Keys. Erwartet: {required_keys}, Erhalten: {set(profile.keys())}")
            
            # Wertebereich prüfen und clampen auf [-max_value, +max_value]
            # Für 7 Tests: -14 bis +14
            extreme_values_used = []
            for key in required_keys:
                value = profile[key]
                if not isinstance(value, (int, float)):
                    raise AIProfileError(f"Ungültiger Wert für {key}: {value} (muss numerisch sein)")
                
                # Konvertiere zu int und clampe auf erlaubten Bereich
                int_value = int(value)
                clamped_value = max(-max_value, min(max_value, int_value))
                
                # Warnung wenn Wert außerhalb des Bereichs lag
                if int_value != clamped_value:
                    import warnings
                    warnings.warn(
                        f"KI-generierter Wert für {key} ({int_value}) außerhalb des erlaubten Bereichs "
                        f"[{-max_value}, {+max_value}]. Wurde auf {clamped_value} begrenzt.",
                        UserWarning
                    )
                
                # Warnung bei Extremwerten (sollten vermieden werden)
                if clamped_value in [-max_value, max_value]:
                    extreme_values_used.append(f"{key}={clamped_value}")
                
                profile[key] = clamped_value
            
            # Info-Warnung wenn zu viele Extremwerte verwendet wurden
            if len(extreme_values_used) >= 2:
                import warnings
                warnings.warn(
                    f"KI verwendet zu viele Extremwerte: {', '.join(extreme_values_used)}. "
                    f"Empfehlung: Werte zwischen {-max_value+2} und {max_value-2} bevorzugen.",
                    UserWarning
                )
            
            return profile
            
        except APIConnectionError as e:
            raise AIProfileConnectionError(
                f"Verbindung zur OpenAI API fehlgeschlagen: {str(e)}"
            )
        except APITimeoutError as e:
            raise AIProfileConnectionError(
                f"Timeout bei OpenAI API-Anfrage: {str(e)}"
            )
        except RateLimitError as e:
            raise AIProfileError(
                f"Rate Limit erreicht: {str(e)}"
            )
        except json.JSONDecodeError as e:
            raise AIProfileError(
                f"Konnte Response nicht als JSON parsen: {str(e)}"
            )
        except OpenAIError as e:
            raise AIProfileError(
                f"OpenAI API Fehler: {str(e)}"
            )
        except Exception as e:
            raise AIProfileError(
                f"Unerwarteter Fehler: {str(e)}"
            )
    
    def get_assessment(
        self,
        dog_data: DogData,
        ist_profile: Dict[str, int],
        ideal_profile: Dict[str, int],
        owner_profile: Optional[Dict[str, int]] = None,
        test_count: int = 7
    ) -> str:
        """
        Erstellt eine textuelle Bewertung durch Vergleich der Profile
        
        Args:
            dog_data: Stammdaten des Hundes
            ist_profile: Gemessenes Profil aus Tests
            ideal_profile: KI-generiertes Idealprofil
            owner_profile: Optional - Fragebogen-Profil des Halters
            test_count: Anzahl Tests pro Dimension
            
        Returns:
            Textuelle Bewertung als String (mehrere Absätze)
            
        Raises:
            AIProfileConnectionError: Bei Verbindungsproblemen
            AIProfileError: Bei anderen API-Fehlern
        """
        max_value = test_count * 2
        age_total = dog_data.age_years + (dog_data.age_months / 12.0)
        
        # Profile formatieren
        ist_str = ", ".join([f"{k}: {v}" for k, v in ist_profile.items()])
        ideal_str = ", ".join([f"{k}: {v}" for k, v in ideal_profile.items()])
        owner_str = ", ".join([f"{k}: {v}" for k, v in owner_profile.items()]) if owner_profile else "Nicht vorhanden"
        
        prompt = f"""Du bist ein Experte für Hundepsychologie und erstellst professionelle Bewertungen.

Analysiere die folgenden OCEAN-Profile für einen Hund:

**Hundedaten:**
- Name: {dog_data.dog_name}
- Rasse: {dog_data.breed}
- Alter: {age_total:.1f} Jahre
- Geschlecht: {dog_data.gender.value}
- Einsatzgebiet: {dog_data.intended_use}

**IST-Profil (gemessen durch Tests):**
{ist_str}

**IDEAL-Profil (für Rasse und Einsatzgebiet):**
{ideal_str}

**FRAGEBOGEN-Profil (Erwartungen des Halters):**
{owner_str}

Wertebereich: -{max_value} bis +{max_value}

Erstelle eine professionelle Bewertung mit folgenden Aspekten:

1. **Gesamteignung**: Wie gut passt der Hund zum Einsatzgebiet?
2. **Stärken**: Welche positiven Eigenschaften zeigt der Hund?
3. **Entwicklungsbereiche**: Wo gibt es Abweichungen vom Ideal?
4. **Halter-Erwartungen**: Wie passen die Erwartungen zur Realität? (falls vorhanden)
5. **Empfehlungen**: Konkrete Trainings- oder Entwicklungsempfehlungen

Schreibe in professionellem, aber verständlichem Deutsch. Die Bewertung soll konstruktiv und hilfreich sein.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Du bist ein erfahrener Hundepsychologe und erstellst professionelle, konstruktive Bewertungen."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens * 3,  # Längere Response für Assessment
                temperature=0.8
            )
            
            assessment = response.choices[0].message.content.strip()
            return assessment
            
        except APIConnectionError as e:
            raise AIProfileConnectionError(
                f"Verbindung zur OpenAI API fehlgeschlagen: {str(e)}"
            )
        except APITimeoutError as e:
            raise AIProfileConnectionError(
                f"Timeout bei OpenAI API-Anfrage: {str(e)}"
            )
        except RateLimitError as e:
            raise AIProfileError(
                f"Rate Limit erreicht: {str(e)}"
            )
        except OpenAIError as e:
            raise AIProfileError(
                f"OpenAI API Fehler: {str(e)}"
            )
        except Exception as e:
            raise AIProfileError(
                f"Unerwarteter Fehler: {str(e)}"
            )
