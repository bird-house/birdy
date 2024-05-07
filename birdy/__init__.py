# noqa: D100, D104

__version__ = "0.8.7"

from .client import WPSClient
from .ipyleafletwfs import IpyleafletWFS  # noqa: F401

# backwards compatibility
import_wps = BirdyClient = WPSClient
