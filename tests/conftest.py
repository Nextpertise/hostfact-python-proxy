import sys
import os

# Add the src directory to the path.
# This allows tests to import app from main.py in the src directory.
# This enables: poetry run pytest
sys.path.append(os.path.abspath("src"))