import sys
import dns.resolver
import pandas as pd
import numpy as np
import tldextract as tld
import whois
import datetime

from disinfo_net.postgres.pg import DisinfoRawDataDB
from disinfo_net.util.ip_util.network_info import NetworkInfo
from disinfo_net.util.html_util.snapshot_info import SnapshotInfo

class WhoisFeatures():

    network_info = NetworkInfo()
    snapshot_info = SnapshotInfo()
    proxy_keywords = ["redacted", "proxy", "guard", "whois", "privacy", "protect", "domain"]
    training_insertion_date = datetime.date(2019, 3, 6)
    
    @staticmethod
    def get_feature_names():
        global_info = globals()["WhoisFeatures"]
        members = dir(global_info)
        feature_names = []
        for member in members:
            if "ft_" in member:
                feature_names += [member]
        return feature_names

    @staticmethod
    def get_features(feature_names, raw_data, available, domain):
        # Load WHOIS string into an object
        try:
            raw_data = whois.WhoisEntry.load(domain, raw_data)
        except Exception as e:
            raw_data = None

        # Get features from the WHOIS record
        features = {}
        for feature_name in feature_names:
            if feature_name == "ft_nameserver_ip_info":
                (nameserver, ip) = WhoisFeatures.lookup_nameserver_ip(raw_data)
                val = WhoisFeatures.ft_nameserver_ip_info(ip)
                features["nameserver asn"] = val[0]
                features["nameserver geoloc"] = val[1]
            else:
                module = globals()["WhoisFeatures"]
                feature_func = getattr(module, feature_name)
                kwargs = {"raw_data": raw_data, "available": available, "domain": domain}
                val = feature_func(**kwargs)
                feature_name = feature_name.replace("ft_", "")
                feature_name = feature_name.replace("_", " ")
                features[feature_name] = val
        df = pd.DataFrame(index=[domain], data=features)
        return df

    @staticmethod
    def get_expiration_date (raw_data=None, available=False, domain=""):
        if raw_data is None or 'expiration_date' not in raw_data or not available:
            return None

        # Type check
        expiration_date = raw_data['expiration_date']
        if expiration_date is None or isinstance(expiration_date, str):
            return None
        elif isinstance(expiration_date, list):
            expiration_date = expiration_date[0]
        return expiration_date.date()

    @staticmethod
    def get_creation_date (raw_data=None, available=False, domain=""):
        if raw_data is None or 'creation_date' not in raw_data or not available:
            return None

        # Type check
        creation_date = raw_data['creation_date']
        if creation_date is None or isinstance(creation_date, str):
            return None
        elif isinstance(creation_date, list):
            creation_date = creation_date[0]
        return creation_date.date()

    @staticmethod
    def get_updated_date (raw_data=None, available=False, domain=""):
        if raw_data is None or 'updated_date' not in raw_data or not available:
            return None

        # Type check
        updated_date = raw_data['updated_date']
        if updated_date is None or isinstance(updated_date, str):
            return None
        elif isinstance(updated_date, list):
            updated_date = updated_date[0]
        return updated_date.date()

    @staticmethod
    def has_whois (raw_data=None, available=False, domain=""):
        if pd.isna(raw_data):
            return "False"
        return "True"

    @staticmethod
    def lookup_nameserver_ip(raw_data):
        if raw_data is None or 'name_servers' not in raw_data:
            return (None, None)

        nameservers = raw_data['name_servers']
        if nameservers is None:
            return (None, None)

        nameserver = nameservers[0]
        try:
            answers = dns.resolver.query(nameserver, 'A').rrset
            ip = str(answers[0])
        except KeyboardInterrupt:
            exit(0)
        except Exception as e:
            ip = None
        return (nameserver, ip)

    @staticmethod
    def ft_registrar(raw_data=None, available=False, domain=""):
        if raw_data is None or 'registrar' not in raw_data:
            return None

        if type(raw_data['registrar']) is list:
            return None        
        return raw_data['registrar']

    @staticmethod
    def ft_registrant_country(raw_data=None, available=False, domain=""):
        if raw_data is None or 'country' not in raw_data:
            return None

        if type(raw_data['country']) is list:
            return None
        return raw_data['country']

    @staticmethod
    def ft_registrant_org(raw_data=None, available=False, domain=""):
        if raw_data is None or 'org' not in raw_data:
            return None

        if type(raw_data['org']) is list:
            return None        
        return raw_data['org']
    
    @staticmethod
    def ft_nameserver_sld(raw_data=None, available=False, domain=""):
        if raw_data is None or 'name_servers' not in raw_data:
            return None

        nameservers = raw_data['name_servers']
        if nameservers is None:
            return None

        ns = nameservers[0]
        ns_lower = ns.lower()
        ext = tld.extract(ns_lower)
        sld = ext.domain + "." + ext.suffix
        return sld
   
    @staticmethod
    def ft_nameserver_ip_info(nameserver_ip):
        if nameserver_ip is None:
            return (None, None)

        nameserver_ip = str(nameserver_ip)
        resp = WhoisFeatures.network_info.ip_lookup(nameserver_ip)

        return (str(resp.asn), str(resp.geoloc))
    
    @staticmethod
    def ft_creation_elapsed_time (raw_data=None, available=False, domain=""):
        # Compute elapsed time from creation date
        creation_date = WhoisFeatures.get_creation_date(raw_data, available, domain)
        if not creation_date:
            return np.nan
       
        # If the domain has a snapshot date, normalize the elapsed time
        snapshot_date = WhoisFeatures.snapshot_info.get_snapshot_date(domain)
        if snapshot_date and snapshot_date != "None":
            now = datetime.datetime.strptime(snapshot_date, "%Y%m%d").date()
        else:
            now = WhoisFeatures.training_insertion_date 

        elapsed_time = now - creation_date
        return elapsed_time.days
    
    @staticmethod
    def ft_time_to_expiration (raw_data=None, available=False, domain=""):
        # Compute time to expiration
        expiration_date = WhoisFeatures.get_expiration_date(raw_data, available, domain)
        if not expiration_date:
            return np.nan

        # If the domain has a snapshot date, normalize the elapsed time
        snapshot_date = WhoisFeatures.snapshot_info.get_snapshot_date(domain)
        if snapshot_date and snapshot_date != "None":
            now = datetime.datetime.strptime(snapshot_date, "%Y%m%d").date()
        else:
            now = WhoisFeatures.training_insertion_date
        
        time_to_expiration = expiration_date - now
        return time_to_expiration.days

    @staticmethod
    def ft_time_from_updated (raw_data=None, available=False, domain=""):
        # Compute elapsed time from updated date
        updated_date = WhoisFeatures.get_updated_date(raw_data, available, domain)
        if not updated_date:
            return np.nan

        # If the domain has a snapshot date, normalize the elapsed time
        snapshot_date = WhoisFeatures.snapshot_info.get_snapshot_date(domain)
        if snapshot_date and snapshot_date != "None":
            now = datetime.datetime.strptime(snapshot_date, "%Y%m%d").date()
        else:
            now = WhoisFeatures.training_insertion_date
        
        time_from_updated = now - updated_date
        return time_from_updated.days
    
    @staticmethod
    def ft_whois_lifetime (raw_data=None, available=False, domain=""):
        # Compute time between creation date and expiration date
        creation_date = WhoisFeatures.get_creation_date(raw_data, available, domain)
        expiration_date = WhoisFeatures.get_expiration_date(raw_data, available, domain)
        if not creation_date or not expiration_date:
            return np.nan

        lifetime = expiration_date - creation_date
        return lifetime.days
    
    @staticmethod
    def ft_domain_proxy (raw_data=None, available=False, domain=""):
        if raw_data is None or 'org' not in raw_data:
            return "N/A"

        org = raw_data["org"]
        if isinstance(org, list) or org is None:
            return "False" 

        org = org.lower()
        if any(keyword in org for keyword in WhoisFeatures.proxy_keywords):
            return "True"
        return "False"
