__version__ = '0.4.2'

from .client.base import WPSClient

# backward compatiblitiy
import_wps = BirdyClient = WPSClient
