"""
Root Workspace Launcher for VisionFit AI
Allows running `streamlit run app.py` directly from project root directory.
"""

import sys
from pathlib import Path

# Add visionfit-ai folder to sys.path
visionfit_dir = Path(__file__).resolve().parent / "visionfit-ai"
if str(visionfit_dir) not in sys.path:
    sys.path.insert(0, str(visionfit_dir))

# Change working directory so relative paths (assets/custom.css, visionfit.db) resolve smoothly
import os
os.chdir(str(visionfit_dir))

# Import and execute main visionfit app
from app import *

