import sys
import csv
import numpy as np
import pandas as pd

from disinfo_net.features.data_fetcher import RawDataFetcher
from disinfo_net.postgres.pg import DisinfoTrainingDB
from disinfo_net.postgres.pg import DisinfoTrainingResp

TRAINING_DATA_DIR = "../data/training/"
DISINFORMATION_DOMAINS = TRAINING_DATA_DIR + "disinformation_domains.csv"
NEWS_DOMAINS = TRAINING_DATA_DIR + "news_domains.csv"
NON_NEWS_DOMAINS = TRAINING_DATA_DIR + "non_news_domains.csv"

class TrainingDataScraper():
    def __init__(self, db_init_file):
        self.db = DisinfoTrainingDB.init_from_config_file(db_init_file)

    def fetch_raw_data_for_domain(self, domain):
        certificate = RawDataFetcher.fetch_certificate(domain)
        whois = RawDataFetcher.fetch_whois(domain)
        html = RawDataFetcher.fetch_html(domain)
        dns = RawDataFetcher.fetch_dns(domain)
        return certificate, whois, html, dns
    
    def scrape(self, domains):
        for domain in domains.index:
            if self.db.check_domain_in_db(domain):
                continue
            
            cert, whois, html, dns = self.fetch_raw_data_for_domain(domain)
            success = self.db.insert_domain(domain, target="news", certificate=cert,
                                            whois=whois, html=html, dns=dns)
            if not success:
                raise Exception
            else:
                print("Scraped: " + domain)

    @staticmethod
    def load_domains (disinformation_domains, news_domains, non_news_domains):
        dtypes = {"host": np.object, "source": np.object,
                  "url": np.object, "available": np.bool,
                  "labeller": np.object, "archive": np.object,
                  "snapshot_date": np.object, "target": np.object}
        disinformation_df = pd.read_csv(disinformation_domains, index_col='host', dtype=dtypes)
        news_df = pd.read_csv(news_domains, index_col='host', dtype=dtypes)
        non_news_df = pd.read_csv(non_news_domains, index_col='host', dtype=dtypes)
        df = pd.concat([disinformation_df, news_df, non_news_df], axis=0)

        # Remove duplicate entries
        df = df[~df.index.duplicated(keep='first')]

        # If a website is unavailable and doesn't have a historical snapshot, remove it
        unusable = (df["available"] == False) & (df["snapshot_date"] == "None")
        df = df[~unusable]
        
        df = pd.concat([disinformation_df, news_df, non_news_df], axis=0)
        return df

if __name__ == '__main__':
    db_init_file = "../data/cred/training_data_cred.ini"
    scraper = TrainingDataScraper(db_init_file)
    domains = TrainingDataScraper.load_domains(DISINFORMATION_DOMAINS,
                                               NEWS_DOMAINS,
                                               NON_NEWS_DOMAINS)
    scraper.scrape(domains)
