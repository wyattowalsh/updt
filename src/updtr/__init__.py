"""Universal package dependency tracker and updater."""

__version__ = "0.1.0"

from .models.config import UpdtConfig
from .updater import UpdateManager

__all__ = ["UpdtConfig", "UpdateManager", "__version__"]
