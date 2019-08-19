__version__ = '0.6.5'

from .client import WPSClient

# backward compatiblitiy
import_wps = BirdyClient = WPSClient
