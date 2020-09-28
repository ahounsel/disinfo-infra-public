import json
from multiprocessing import Process

from disinfo_net.postgres.pg import DisinfoRawDataDB, DisinfoClassificationDB
from disinfo_net.classify.classifier import DisinformationClassifier

class ClassifierThread(Process):
    def __init__(self, raw_data_db_file, classification_db_file, model_file, queue):
        super().__init__()
        self.raw_data_db_file = raw_data_db_file
        self.classification_db_file = classification_db_file
        self.model_file = model_file
        self.queue = queue

    def thread_init(self):
        self.classifier = DisinformationClassifier.load_model_from_file(self.model_file)
        self.rdb = DisinfoRawDataDB.init_from_config_file(self.raw_data_db_file)
        self.cdb = DisinfoClassificationDB.init_from_config_file(self.classification_db_file)

    def run(self):
        self.thread_init()
        while(1):
            try:
                domain = self.queue.get()
                resp = self.rdb.query_domain(domain)
                classification, probs = self.classifier.predict(resp)
                probs = json.dumps(probs)
                self.cdb.insert_domain(domain, classification, probs)
                print(domain, classification)
            except Exception as e:
                print('Error in classification thread: {0}'.format(e))
