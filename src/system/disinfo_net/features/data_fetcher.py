import socket
import ssl
import whois
import requests
import dns.resolver

class RawDataFetcher:
    def __init__(self):
        pass

    @staticmethod
    def fetch_certificate(domain):
        try:
            # Get the certificate
            context = ssl._create_unverified_context()
            sock = socket.socket(socket.AF_INET)
            sock.settimeout(5)
            conn = context.wrap_socket(sock,
                                       server_hostname=domain)
            conn.connect((domain, 443))
            der_cert = conn.getpeercert(True)

            # Convert the certificate from DER to PEM
            raw_data = str(ssl.DER_cert_to_PEM_cert(der_cert))
        except Exception as e:
            raw_data = None
        
        return raw_data

    @staticmethod
    def fetch_whois(domain):
        try:
            obj = whois.whois(domain)
            raw_data = obj.text
        except Exception as e:
            raw_data = None

        return raw_data
 
    @staticmethod
    def fetch_html(domain):
        try:
            raw_data = requests.get('http://' + domain, timeout=10).text
        except Exception as e:
            raw_data = None

        return raw_data

    @staticmethod
    def fetch_dns(domain):
        try:
            raw_data = dns.resolver.query(domain, 'A').rrset[0]
            raw_data = str(raw_data)
        except Exception as e:
            raw_data = None

        return raw_data
