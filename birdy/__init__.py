__version__ = '0.7.0'

from .client import WPSClient

# backward compatiblitiy
import_wps = BirdyClient = WPSClient
