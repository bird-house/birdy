__version__ = "0.7.0"

from .client import WPSClient
from .ipyleafletwfs import IpyleafletWFS  # noqa: F401

# backward compatiblitiy
import_wps = BirdyClient = WPSClient
