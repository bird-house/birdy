__version__ = '0.6.7'

from .client import WPSClient

# backward compatiblitiy
import_wps = BirdyClient = WPSClient
