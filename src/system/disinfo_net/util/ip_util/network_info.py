import os
from collections import namedtuple

import sys

import pyasn
import geoip2.database

import pkg_resources

ASN_DB = 'pyasn.dat'
GEO_DB = 'GeoLite2-Country.mmdb'

class NetworkInfo:
    IpInfo = namedtuple('IpAddressInfo', 'asn, cidr, geoloc')
    
    def __init__(self):
        resource_package = __name__  
        af = pkg_resources.resource_filename(resource_package, '/{0}'.format(ASN_DB))
        self.asndb = pyasn.pyasn(af)
        gf = pkg_resources.resource_filename(resource_package, '/{0}'.format(GEO_DB))
        self.geodb = geoip2.database.Reader(gf)

    def ip_lookup(self, ip):
        asn = None,
        cidr = None
        try:
             asn, cidr = self.asndb.lookup(ip)
        except Exception as e:
            pass

        iso = None
        try: 
            response = self.geodb.country(ip)
            if response:
                iso = response.country.iso_code
        except Exception as e:
            pass
    
        return NetworkInfo.IpInfo(asn, cidr, iso)

    def network_lookup(self, cidr):
        pass
