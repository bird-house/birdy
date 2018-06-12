




from owslib import wps

fp = wps.WebProcessingService(url='http://pavics.ouranos.ca/twitcher/ows/proxy/flyingpigeon/wps', skip_caps=True,  )

fp.getcapabilities()