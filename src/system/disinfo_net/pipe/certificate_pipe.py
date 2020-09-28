from time import sleep

import certstream

from disinfo_net.pipe.domain_pipe import DomainPipe
from disinfo_net.util.domain_util.url_parser import UrlParser


class CertificatePipe(DomainPipe):
    def __init__(self):
        super().__init__()

    def run(self):
        certstream.listen_for_events(self.process_event,
                                     'wss://certstream.calidog.io')

    def initialize_connection(self, cred_file=None):
        pass
    
    def process_event(self, message, context):
        try:
            if message['message_type'] != 'certificate_update':
                return
 
            index = message['data']['cert_index'] 
            all_domains = message["data"]["leaf_cert"]["all_domains"]
            domain_set = set()
            for domain in all_domains:
                domain = UrlParser.strip_url(domain)
                if domain not in domain_set:
                    self.queue.put((domain, index, 'certstream'))
                    domain_set.add(domain)
        except Exception as e:
            pass

    def set_queue(self, q):
        self.queue = q
