"""
Launcher für Test-Data-Eingabe Demo
"""
import sys
from pathlib import Path

# Füge Projekt-Root zum Path hinzu
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.demo_test_data import main

if __name__ == "__main__":
    main()
