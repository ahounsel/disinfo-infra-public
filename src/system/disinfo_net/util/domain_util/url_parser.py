from unshortenit import UnshortenIt
import tldextract
from urllib.parse import urlparse

class UrlParser: 
    def __init__(self):
        self.unshortener = UnshortenIt()
            
    @staticmethod
    def strip_url(url):
        result = tldextract.extract(url)

        new_url = result.domain + '.' + result.suffix

        return new_url.lower()
 
    def unshorten_url(self, url):
        try:
            new_url = self.unshortner.unshorten(url)
        except Exception as e:
            new_url = url
        
        return new_url.lower()
