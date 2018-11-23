__version__ = '0.4.2'

from .client import WPSClient

# backward compatiblitiy
import_wps = BirdyClient = WPSClient
