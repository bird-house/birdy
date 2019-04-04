__version__ = '0.6.0'

from .client import WPSClient

# backward compatiblitiy
import_wps = BirdyClient = WPSClient
