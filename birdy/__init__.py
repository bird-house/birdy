__version__ = "0.6.8"

from .client import WPSClient
from .ipyleafletwfs import IpyleafletWFS  # noqa: F401

# backward compatiblitiy
import_wps = BirdyClient = WPSClient
