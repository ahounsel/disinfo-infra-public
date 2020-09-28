import sys
import csv
import pandas as pd
import numpy as np
import tldextract
import dns.resolver
import json
import datetime

from disinfo_net.postgres.pg import DisinfoRawDataDB
from disinfo_net.util.ip_util.network_info import NetworkInfo
from disinfo_net.util.domain_util.tld_info import TldInfo
from disinfo_net.util.domain_util.newsy_info import NewsyInfo

class DomainFeatures():

    network_info = NetworkInfo()
    newsy_info = NewsyInfo()
    tld_info = TldInfo()

    @staticmethod
    def get_feature_names():
        global_info = globals()["DomainFeatures"]
        members = dir(global_info)
        feature_names = []
        for member in members:
            if "ft_" in member:
                feature_names += [member]
        return feature_names

    @staticmethod
    def get_features(feature_names, raw_data, available, domain):
        # Get features from the A record
        features = {}
        for feature_name in feature_names:
            if feature_name == "ft_domain_ip_info":
                val = DomainFeatures.ft_domain_ip_info(raw_data)
                features["domain asn"] = val[0]
                features["domain geoloc"] = val[1]
            else:
                module = globals()["DomainFeatures"]
                feature_func = getattr(module, feature_name)
                kwargs = {"raw_data": raw_data, "available": available, "domain": domain}
                val = feature_func(**kwargs)
                feature_name = feature_name.replace("ft_", "")
                feature_name = feature_name.replace("_", " ")
                features[feature_name] = val
        df = pd.DataFrame(index=[domain], data=features)
        return df

    @staticmethod
    def ft_has_domain_ip (raw_data=None, available=False, domain=""):
        if pd.isna(raw_data):
            return "False"
        return "True"

    @staticmethod
    def ft_domain_ip_info(raw_data=None, available=False, domain=""):
        if pd.isna(raw_data):
            return (None, None)

        ip = str(raw_data)
        response = DomainFeatures.network_info.ip_lookup(ip)
        return (str(response.asn), str(response.geoloc))

    @staticmethod
    def ft_contains_digit (raw_data=None, available=False, domain=""):
        return str(any(char.isdigit() for char in domain))
    
    @staticmethod
    def ft_contains_hyphen (raw_data=None, available=False, domain=""):
        return str(any(char == "-" for char in domain))
    
    @staticmethod
    def ft_length (raw_data=None, available=False, domain=""):
        return len(domain)
    
    @staticmethod
    def ft_novelty_tld (raw_data=None, available=False, domain=""):
        # Extract the TLD from the domain name
        try:
            ext = tldextract.extract(domain)
            tld = ext.suffix
        except:
            return "False"

        # Check if the TLD is uncommon
        if tld in DomainFeatures.tld_info.cctld_list or tld in DomainFeatures.tld_info.gtld_list:
            return "False"
        return "True"

    @staticmethod
    def ft_contains_news(raw_data=None, available=False, domain=""):
        try:
            ext = tldextract.extract(domain)
            sld = ext.domain
        except:
            return "False"

        # Check if newsy token is in the SLD
        if "news" in sld:
            return "True"
        return "False"
    
    @staticmethod
    def ft_newsy_domain(raw_data=None, available=False, domain=""):
        newsy_tokens = DomainFeatures.newsy_info.newsy_tokens
        try:
            ext = tldextract.extract(domain)
            sld = ext.domain
        except:
            return "False"

        # Check if newsy token is in the SLD
        for token in newsy_tokens:
            if token in sld:
                return "True"
        return "False"
