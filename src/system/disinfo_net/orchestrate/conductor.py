from multiprocessing import Queue

from disinfo_net.orchestrate.data_fetcher_thread import DataFetcherThread
from disinfo_net.classify.classifier import DisinformationClassifier

class Conductor:
    def __init__(self):
        self.pipes = {}
        self.auto_pipe_label = 0
        self.firehose = None

    def add_firehose_pipe(self, pipe, label=None):
        if label is not None:
            self.pipes[label] = pipe
        else:
            self.pipes[self.auto_pipe_label] = pipe
            self.auto_pipe_label += 1

    def start_firehose_pipes(self):
        self.firehose = Queue()
        for p in self.pipes.values():
            p.set_queue(self.firehose)
            p.start()

    def start(self, database_init_file, num_threads=1):
        if not self.firehose:
            self.start_firehose_pipes()

        for i in range(0, num_threads):
            w = DataFetcherThread(i, self.firehose, database_init_file)
            w.start()
