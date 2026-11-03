import sys
from pathlib import Path

# `make proto` writes generated code to ./gen; make it importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gen"))
