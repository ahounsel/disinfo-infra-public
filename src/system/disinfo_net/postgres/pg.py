import datetime

import psycopg2
from configparser import ConfigParser

from abc import ABC, abstractmethod

class DisinfoDB(ABC):
    def __init__(self, database, user, password, host, table_name):
        self.table_name = table_name
        try:
            self.conn = psycopg2.connect(host=host, database=database, user=user, 
                                         password=password)
        except Exception as e:
            print('Error connection to database: {0}'.format(e)) 
        try:
            self.cursor = self.conn.cursor()
        except Exception as e:
            print('Error getting cursor form database: {0}'.format(e))
    
    @staticmethod
    @abstractmethod
    def init_from_config_file(cf, section='postgresql'):
        pass
    
    @staticmethod
    def _read_config_file(cf, section='postgresql'):
        parser = ConfigParser()
        parser.read(cf)
    
        params = {}
        if parser.has_section(section):
            for param in parser.items(section):
                params[param[0]] = param[1]

        return params
    
        return DisinfoDB(database=params['database'], user=params['user'], 
                         password=params['password'], host=params['host'])


    def delete_table(self):
        ans = input('Delete table: {0} from database? (Y/n): '.format(self.table_name))
        if ans == 'Y':
            cmd = 'DROP TABLE {0}'.format(self.table_name)
            self._execute_command(cmd)
    
    def _execute_command(self, cmd, format_tuple=None):
        try:
            if format_tuple:
                self.cursor.execute(cmd, format_tuple)
            else:
                self.cursor.execute(cmd)
            self.conn.commit()
        except Exception as e:
            print('Error executing command: {0}, error: {1}'.format(cmd, e))
            return False

        return True
    
    def check_domain_in_db(self, domain):
        s = 'SELECT domain FROM {0} WHERE domain=%s'.format(self.table_name)
        ft = (domain,)
        self._execute_command(s, ft)
        row = self.cursor.fetchone()

        if row:
            return True
        else:
            return False
    
    def query_custom(self, query, format_tuple=None):
        self._execute_command(query, format_tuple)
        rows = self.cursor.fetchall()
        
        return rows

    def query_num_domains(self):
        s = 'SELECT domain FROM {0}'.format(self.table_name)
        self._execute_command(s) 
        rows = self.cursor.fetchall() 
    
        return len(rows)
    
    def close(self):
        self.cursor.close()
        self.conn.close()
 
    @abstractmethod
    def create_table(self):
        pass
    
    @abstractmethod
    def query_domain(self, domain):
        pass

    @abstractmethod
    def insert_domain(self, domain):
        pass

class DisinfoRawDataDB(DisinfoDB):
    def __init__(self, database, user, password, host, table_name):
        super().__init__(database, user, password, host, table_name)
    
    @staticmethod
    def init_from_config_file(cf, section='postgresql'):
        params = DisinfoDB._read_config_file(cf, section=section)
        
        return DisinfoRawDataDB(params['database'], 
                                params['user'], 
                                params['password'],
                                params['host'],
                                params['table_name'])

    def create_table(self):
        s = '''
            CREATE TABLE {0} (
                domain TEXT PRIMARY KEY,
                certificate TEXT,
                whois TEXT,
                html TEXT,
                dns TEXT,
                post_id TEXT,
                platform TEXT,
                insertion_time TIMESTAMP
                )'''.format(self.table_name)
        
        self._execute_command(s)

    def query_domain(self, domain):
        s = 'SELECT domain, certificate, whois, html, dns, post_id, platform, insertion_time FROM {0} WHERE domain=%s'.format(self.table_name)
        self._execute_command(s, (domain,))
        
        row = self.cursor.fetchone()
        if row:
            resp = DisinfoRawDataResp(*row)
            return resp
        else:
            return None

    def insert_domain(self, domain, certificate=None,
                      whois=None, html=None, dns=None, post_id=None, 
                      platform=None):
        domain_insert = ''' INSERT INTO {0}(domain, certificate, whois, html, dns, post_id, platform, insertion_time)
                            VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (domain)
                            DO NOTHING'''.format(self.table_name)
    
        now = datetime.datetime.utcnow()
        tup = (domain, certificate, whois, html, dns, post_id, 
               platform, now) 
        rv = self._execute_command(domain_insert, tup)

        return rv

class DisinfoRawDataResp:
    def __init__(self, domain, certificate, whois, html, dns,
                 post_id, platform, insertion_time):
        self.domain = domain
        self.certificate = certificate
        self.whois = whois
        self.html = html
        self.dns = dns
        self.post_id = post_id
        self.platform = platform
        self.insertion_time = insertion_time

class DisinfoClassificationDB(DisinfoDB):
    def __init__(self, database, user, password, host, table_name):
        super().__init__(database, user, password, host, table_name)

    @staticmethod
    def init_from_config_file(cf, section='postgresql'):
        params = DisinfoDB._read_config_file(cf, section=section)
        
        return DisinfoClassificationDB(params['database'], 
                                       params['user'], 
                                       params['password'],
                                       params['host'],
                                       params['table_name'])

    def create_table(self):
        s = '''
        CREATE TABLE {0} (
            domain TEXT PRIMARY KEY,
            classification TEXT,
            probabilities JSON,
            insertion_time TIMESTAMP
        )'''.format(self.table_name)

        rv = self._execute_command(s)

    def insert_domain(self, domain, classification, probabilities):
        insert = ''' INSERT INTO {0}(domain, classification, probabilities, insertion_time)
                     VALUES(%s, %s, %s, %s)
                     ON CONFLICT (domain)
                     DO NOTHING'''.format(self.table_name)
        
        now = datetime.datetime.utcnow()
        tup = (domain, classification, probabilities, now)
        rv = self._execute_command(insert, tup)

        return rv

    def query_domain(self, domain):
        s = 'SELECT * FROM {0} WHERE domain=%s'.format(self.table_name)
        self._execute_command(s, (domain,))
        
        row = self.cursor.fetchone()
        print(row)

        if row:
            return DisinfoClassificationResp(*row)
        else:
            return None


class DisinfoClassificationResp:
    def __init__(self, domain, classification, probabilities, insertion_time):
        self.domain = domain
        self.classification = classification
        self.probabilities = probabilities
        self.insertion_time = insertion_time

class DisinfoTrainingDB(DisinfoDB):
    def __init__(self, database, user, password, host, table_name):
        super().__init__(database, user, password, host, table_name)

    @staticmethod
    def init_from_config_file(cf, section='postgresql'):
        params = DisinfoDB._read_config_file(cf, section=section)
        
        return DisinfoTrainingDB(params['database'], 
                                 params['user'], 
                                 params['password'],
                                 params['host'],
                                 params['table_name'])
    def create_table(self):
        s = '''
        CREATE TABLE {0} (
            domain TEXT PRIMARY KEY,
            target TEXT,
            certificate TEXT,
            whois TEXT,
            html TEXT,
            dns TEXT    
        )'''.format(self.table_name)
        
        rv = self._execute_command(s)

    def insert_domain(self, domain, target, certificate, whois, html, dns):
        insert = ''' INSERT INTO {0}(domain, target, certificate, whois, html, dns)
                     VALUES(%s, %s, %s, %s, %s, %s)
                     ON CONFLICT (domain)
                     DO NOTHING'''.format(self.table_name)
        
        tup = (domain, target, certificate, whois, html, dns)
        rv = self._execute_command(insert, tup)

        return rv

    def remove_domain(self, domain):
        s = 'DELETE FROM {0} WHERE domain=%s'.format(self.table_name)
        rv = self._execute_command(s, (domain,))
        
        return rv

    def query_domain(self, domain):
        s = 'SELECT * FROM {0} WHERE domain=%s'.format(self.table_name)
        self._execute_command(s, (domain,))
        
        row = self.cursor.fetchone()

        if row:
            return DisinfoTrainingResp(*row)
        else:
            return None

    def query_all(self):
        s = 'SELECT * FROM {0}'.format(self.table_name)
        self._execute_command(s)
        
        rows = self.cursor.fetchall() 

        if rows:
            responses = []
            for row in rows:
                resp = DisinfoTrainingResp(*row)
                responses += [resp]
            return responses
        else:
            return None

class DisinfoTrainingResp:
    def __init__(self, domain, target, certificate, whois, html, dns):
        self.domain = domain
        self.target = target
        self.certificate = certificate
        self.whois = whois
        self.html = html
        self.dns = dns
