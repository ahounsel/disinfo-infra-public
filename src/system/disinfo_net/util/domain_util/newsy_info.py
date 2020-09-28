import os
import sys
import pkg_resources

NEWSY_TOKENS_FILE = "newsy_tokens.txt"

class NewsyInfo:
    def __init__(self):
        resource_package = __name__  
        newsy_tokens_file = pkg_resources.resource_filename(resource_package, '/{0}'.format(NEWSY_TOKENS_FILE))
        self.newsy_tokens = self.load_newsy_tokens(newsy_tokens_file)

    def load_newsy_tokens(self, newsy_tokens_file):
        with open (newsy_tokens_file, "r") as f:
            newsy_tokens = list(set(f.read().splitlines()))
        return newsy_tokens
