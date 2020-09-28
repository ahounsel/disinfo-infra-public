#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

from disinfo_net.orchestrate.conductor import Conductor
from disinfo_net.pipe.reddit_pipe import RedditPipe
from disinfo_net.pipe.twitter_pipe import TwitterPipe
from disinfo_net.pipe.certificate_pipe import CertificatePipe
from disinfo_net.pipe.domaintools_pipe import DomaintoolsPipe
from disinfo_net.postgres.pg import DisinfoRawDataDB

def main():
    parser = argparse.ArgumentParser()

    # database arguments
    parser.add_argument('database_config_file')
    parser.add_argument('-cdt', '--create_database_table', action='store_true')
    parser.add_argument('-ddt', '--delete_database_table', action='store_true')

    # firehose options
    parser.add_argument('-rcf', '--reddit_cred_file', default=None)
    parser.add_argument('-tcf', '--twitter_cred_file', default=None)
    parser.add_argument('-cp', '--certificate_pipe', action='store_true')
    parser.add_argument('-dtf', '--domaintools_cred_file', default=None)

    # classifier if we want to classify data we get
    parser.add_argument('-nt', '--num_threads', type=int, default=1)
    args = parser.parse_args()

    if args.create_database_table or args.delete_database_table:
        d = DisinfoRawDataDB.init_from_config_file(args.database_config_file)
        if args.delete_database_table:
            d.delete_table()
        if args.create_database_table:
            d.create_table()
        d.close()
    
    c = Conductor()
    if args.reddit_cred_file:
        r = RedditPipe(args.reddit_cred_file)
        c.add_firehose_pipe(r, 'reddit')

    if args.twitter_cred_file:
        t = TwitterPipe(args.twitter_cred_file)
        c.add_firehose_pipe(t, 'twitter')

    if args.certificate_pipe:
        cp = CertificatePipe()
        c.add_firehose_pipe(cp, 'cert')

    if args.domaintools_cred_file:
        dt = DomaintoolsPipe(args.domaintools_cred_file)
        c.add_firehose_pipe(dt, 'domaintools')

    # add pipes here if you want

    if not c.pipes:
        print('No domain pipes for candidate domains, exiting')
        return

    c.start(args.database_config_file, num_threads=args.num_threads)

if __name__ == '__main__':
    main()
