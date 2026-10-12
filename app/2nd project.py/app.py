"""
VisionFit AI - Launcher Bridge
Redirects execution to the visionfit-ai package.
"""

import sys
from pathlib import Path

# Add visionfit-ai to python path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
VISIONFIT_DIR = ROOT_DIR / "visionfit-ai"

if str(VISIONFIT_DIR) not in sys.path:
    sys.path.insert(0, str(VISIONFIT_DIR))

# Import and run the main VisionFit app
from app import main

if __name__ == "__main__":
    main()
