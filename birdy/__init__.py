__version__ = '0.6.9'

from .client import WPSClient

# backward compatiblitiy
import_wps = BirdyClient = WPSClient
