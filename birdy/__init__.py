__version__ = '0.5.1'

from .client import WPSClient

# backward compatiblitiy
import_wps = BirdyClient = WPSClient
