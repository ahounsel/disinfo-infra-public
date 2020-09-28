import os
import sys
import pkg_resources

CCTLD_FILE = "cctld.txt"
GTLD_FILE = "gtld.txt"

class TldInfo:
    def __init__(self):
        resource_package = __name__  
        cctld_file = pkg_resources.resource_filename(resource_package, '/{0}'.format(CCTLD_FILE))
        self.cctld_list = self.load_cctld_file(cctld_file)
        gtld_file = pkg_resources.resource_filename(resource_package, '/{0}'.format(GTLD_FILE))
        self.gtld_list = self.load_gtld_file(gtld_file)

    def load_cctld_file(self, cctld_file):
        with open (cctld_file, "r") as f:
            cctld_list = list(set(f.read().splitlines()))
        return cctld_list

    def load_gtld_file(self, gtld_file):
        with open (gtld_file, "r") as f:
            gtld_list = list(set(f.read().splitlines()))
        return gtld_list        
