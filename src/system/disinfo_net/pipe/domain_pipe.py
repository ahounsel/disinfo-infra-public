from abc import ABC, abstractmethod

from disinfo_net.util.domain_util.url_parser import UrlParser
from multiprocessing import Process

class DomainPipe(ABC, Process):
    def __init__(self):
        super().__init__()
        self.url_parser = UrlParser()
        self.queue = None

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def initialize_connection(self, cred_file=None):
        pass

    def set_queue(self, q):
        self.queue = q

    def load_credentials(self, cred_file):
        creds = {}
        with open(cred_file, 'r') as f:
            for line in f:
                name, val = line.strip().split(',')
                creds[name] = val

        return creds
