__version__ = '0.5.0'

from .client import WPSClient

# backward compatiblitiy
import_wps = BirdyClient = WPSClient
