import os
import sys
import pkg_resources
import pandas as pd

DATES_FILE = "snapshot_dates.csv"

class SnapshotInfo:
    def __init__(self):
        resource_package = __name__ 
        dates_file = pkg_resources.resource_filename(resource_package, '/{0}'.format(DATES_FILE))
        self.snapshot_dates = self.load_snapshot_dates(dates_file)

    def load_snapshot_dates(self, dates_file):
        snapshot_dates = pd.read_csv(dates_file, index_col=["host"], usecols=["host", "snapshot_date", "target"])
        snapshot_dates = snapshot_dates[~snapshot_dates.index.duplicated(keep="first")]
        return snapshot_dates

    def get_snapshot_date(self, domain):
        if domain not in self.snapshot_dates.index:
            return None

        snapshot_date = self.snapshot_dates.loc[domain, "snapshot_date"]
        return snapshot_date
        
