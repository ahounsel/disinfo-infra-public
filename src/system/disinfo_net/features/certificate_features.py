import sys
import socket
import ssl
import pandas as pd
import numpy as np
import datetime
import tldextract
from OpenSSL import crypto

from disinfo_net.util.html_util.snapshot_info import SnapshotInfo
from disinfo_net.postgres.pg import DisinfoRawDataDB


class CertificateFeatures():

    snapshot_info = SnapshotInfo()
    training_insertion_date = datetime.date(2019, 3, 6)

    @staticmethod
    def get_feature_names():
        global_info = globals()["CertificateFeatures"]
        members = dir(global_info)
        feature_names = []
        for member in members:
            if "ft_" in member:
                feature_names += [member]
        return feature_names

    @staticmethod
    def get_features(feature_names, raw_data, available, domain):
        # Get features from the certificate
        cert = None
        if raw_data is not None:
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, raw_data)

        features = {}
        for feature_name in feature_names:
            module = globals()["CertificateFeatures"]
            feature_func = getattr(module, feature_name)
            kwargs = {"cert": cert, "available": available, "domain": domain}
            val = feature_func(**kwargs)
            feature_name = feature_name.replace("ft_", "")
            feature_name = feature_name.replace("_", " ")
            features[feature_name] = val
        df = pd.DataFrame(index=[domain], data=features)
        return df

    @staticmethod
    def ft_has_cert (cert=None, available=False, domain=""):
        if pd.isna(cert):
            return "False"
        return "True"

    @staticmethod
    def ft_issuer_country (cert=None, available=False, domain=""):
        if pd.isna(cert):
            return None
        return cert.get_issuer().C

    @staticmethod
    def ft_issuer_org(cert=None, available=False, domain=""):
        if pd.isna(cert):
            return None
        return cert.get_issuer().O

    @staticmethod
    def ft_domain_validated(cert=None, available=False, domain=""):
        if pd.isna(cert):
            return "N/A"

        for i in range(cert.get_extension_count()):
            ext = cert.get_extension(i)
            if ext.get_short_name() == b'certificatePolicies':
                if 'Policy: 2.23.140.1.2.1' in str(ext):
                    return "True"
        return "False"

    @staticmethod
    def ft_has_expired (cert=None, available=False, domain=""):
        if pd.isna(cert) or not available:
            return "N/A"
        
        # If the domain has a snapshot date, normalize the elapsed time
        snapshot_date = CertificateFeatures.snapshot_info.get_snapshot_date(domain)
        if snapshot_date and snapshot_date != "None":
            now = datetime.datetime.strptime(snapshot_date, "%Y%m%d").date()
        else:
            now = CertificateFeatures.training_insertion_date

        not_after_str = cert.get_notAfter()
        not_after = datetime.datetime.strptime(not_after_str.decode("utf-8"), "%Y%m%d%H%M%Sz").date()
        has_expired = (not_after - now).days < 0
        return str(has_expired)

    @staticmethod
    def ft_self_signed (cert=None, available=False, domain=""):
        if pd.isna(cert):
            return "N/A"

        issuer_name = cert.get_issuer().CN
        if issuer_name == domain or issuer_name == 'localhost':
            return "True"
        return "False"

    @staticmethod
    def ft_san_length (cert=None, available=False, domain=""):
        if pd.isna(cert):
            return np.nan

        for i in range(cert.get_extension_count()):
            ext = cert.get_extension(i)
            if ext.get_short_name() == b'subjectAltName':
                san_list = str(ext).split(', ')
                san_sld_set = set()
                for domain in san_list:
                    domain = domain[4:]
                    ext = tldextract.extract(domain)
                    sld = ext.domain + "." + ext.suffix
                    san_sld_set.add(sld)
                return len(san_sld_set)
        return np.nan

    @staticmethod
    def ft_san_contains_wildcard (cert=None, available=False, domain=""):
        if pd.isna(cert):
            return "N/A"

        for i in range(cert.get_extension_count()):
            ext = cert.get_extension(i)
            if ext.get_short_name() == b'subjectAltName':
                san_list = str(ext).split(', ')
                for domain in san_list:
                    if "*" in domain:
                        return "True"
        return "False"

    @staticmethod
    def ft_cert_lifetime(cert=None, available=False, domain=""):
        if pd.isna(cert):
            return np.nan

        not_before = cert.get_notBefore()
        not_after = cert.get_notAfter()
        if not_before is None or not_after is None:
            return np.nan

        format = "%Y%m%d%H%M%SZ"
        not_before = not_before.decode("utf-8")
        not_before = datetime.datetime.strptime(not_before, format).date()
        not_after = not_after.decode("utf-8")
        not_after = datetime.datetime.strptime(not_after, format).date()
        lifetime = (not_after - not_before)
        lifetime = lifetime.days
        return lifetime
