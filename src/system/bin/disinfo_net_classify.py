import csv
import argparse
import datetime
import random
from time import sleep
from multiprocessing import Process, Queue

import psycopg2
import pandas as pd

from disinfo_net.postgres.pg import DisinfoRawDataDB, DisinfoClassificationDB
from disinfo_net.orchestrate.classifier_thread import ClassifierThread

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('raw_data_database_config')
    parser.add_argument('classification_database_config')
    parser.add_argument('model_file')
    parser.add_argument('-l', '--live', action='store_true')
    parser.add_argument('-nt', '--num_threads', type=int, default=1)
    args = parser.parse_args()
    
    run(args.raw_data_database_config, args.classification_database_config,
        args.model_file, args.num_threads, live=args.live) 

def run(raw_db_file, classifcation_db_file, model_file, num_threads, live=False):
    q = Queue()
    for i in range(0, num_threads):
        c = ClassifierThread(raw_db_file, classifcation_db_file, model_file, q)
        c.start()

    db = DisinfoRawDataDB.init_from_config_file(raw_db_file)
    if live: 
        live_loop(db, q)
    else:
        classify_database(db, q)

def classify_database(db, queue):
    q = 'SELECT domain FROM {0}'.format(db.table_name)
    responses = db.query_custom(q)

    print('Classifying (at most): {0} responses'.format(len(responses)))
    [queue.put(r[0]) for r in responses]
    while(1):
        if queue.empty():
            break
        sleep(60)
    
    # Let threads finish
    sleep(30)
    return

def classify_live_sample(db, queue, sample): 
    # Classify live sample
    print('Classifying (at most): {0} responses'.format(len(sample)))
    [queue.put(r[0]) for r in sample]
    while(1):
        if queue.empty():
            break
        sleep(60)
    
    # Let threads finish
    sleep(30)
    return

def live_loop(db, queue):
    q = 'SELECT domain FROM {0} WHERE insertion_time BETWEEN %s and %s'.format(db.table_name)
    while(1):
        now = datetime.datetime.utcnow()
        window = now - datetime.timedelta(minutes=5)
        responses = db.query_custom(q, (window, now))
        print('Classifying {0} responses from last 5 minutes'.format(len(responses)))
        [queue.put(r[0]) for r in responses]
        sleep(5 * 60)
