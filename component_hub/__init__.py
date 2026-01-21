"""
Component Hub. Build Commodore component documentation hub with Antora
"""

from pathlib import Path
from importlib.metadata import version

__version__ = version("component-hub")
__git_version__ = "0"
__install_dir__ = Path(__file__).parent
