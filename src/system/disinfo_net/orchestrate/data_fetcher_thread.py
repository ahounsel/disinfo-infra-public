from multiprocessing import Process

from disinfo_net.features.data_fetcher import RawDataFetcher
from disinfo_net.postgres.pg import DisinfoRawDataDB

class DataFetcherThread(Process):
    def __init__(self, tid, firehose, db_init_file):
        super().__init__()
        self.tid = tid
        self.firehose = firehose 
        self.db_init_file = db_init_file

    def fetch_raw_data_for_domain(self, domain):
        certificate = RawDataFetcher.fetch_certificate(domain)
        whois = RawDataFetcher.fetch_whois(domain)
        html = RawDataFetcher.fetch_html(domain)
        dns = RawDataFetcher.fetch_dns(domain)
        
        return certificate, whois, html, dns
 
    def thread_init(self):
        self.db = DisinfoRawDataDB.init_from_config_file(self.db_init_file) 
    
    def run(self):
        self.thread_init()
        while True:
            try:
                (domain, post_id, platform) = self.firehose.get()
                if self.db.check_domain_in_db(domain):
                    continue 
                cert, whois, html, dns = self.fetch_raw_data_for_domain(domain)
                success = self.db.insert_domain(domain, certificate=cert,
                                                whois=whois, html=html, dns=dns,
                                                post_id=post_id, platform=platform)
                if not success:
                    raise Exception   
            except Exception as e:
                print('Error in worker thread: {0}'.format(e))
                continue
