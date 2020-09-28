#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import time

import domaintools

import disinfo_net.pipe.domain_pipe
from disinfo_net.util.domain_util.newsy_info import NewsyInfo

class DomaintoolsPipe(disinfo_net.pipe.domain_pipe.DomainPipe):
    def __init__(self, cred_file, time_between_runs=7200):
        super().__init__()
        self.newsy_info = NewsyInfo() 
        self.time_between_runs = datetime.timedelta(seconds=time_between_runs)
        self._api = self.initialize_connection(cred_file)

    def initialize_connection(self, cred_file=None):
        credentials = self.load_credentials(cred_file)
        api = domaintools.API(credentials['api_username'], credentials['api_key'])
        return api

    def run(self):
        while True:
            try:
                before = datetime.datetime.utcnow()
                self._add_to_queue()
                after = datetime.datetime.utcnow()
                time.sleep((after - before + self.time_between_runs).total_seconds())
            except Exception as e:
                time.sleep((after - before + self.time_between_runs).total_seconds())

    def _add_to_queue(self):
        if self.queue is None:
            raise Exception("result queue is undefined")
    
        for keyword in self.newsy_info.newsy_tokens:
            with self._api.brand_monitor(query=keyword, domain_status='new') as bm:
                for r in bm:
                    self.queue.put((r['domain'], 'nouniqueindex', 'domaintools'))
