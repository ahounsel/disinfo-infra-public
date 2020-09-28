import argparse

from disinfo_net.postgres.pg import DisinfoTrainingDB
from disinfo_net.classify.classifier import DisinformationClassifier
from disinfo_net.features.whois_features import WhoisFeatures
from disinfo_net.features.certificate_features import CertificateFeatures
from disinfo_net.features.domain_features import DomainFeatures
from disinfo_net.features.webpage_features import WebpageFeatures

full_params     = {'max_features': 196, 
                   'min_samples_split': 5, 
                   'bootstrap': False,
                   'criterion': 'entropy',
                   'n_estimators': 327,
                   'min_samples_leaf': 1,
                   'max_depth': 22,
                   'random_state': 0}

registrar_params = {'max_features': 12,
                    'min_samples_split': 5,
                    'bootstrap': True,
                    'criterion': 'gini',
                    'n_estimators': 245,
                    'min_samples_leaf': 1,
                    'max_depth': 29,
                    'random_state': 0}

ca_params        = {'max_features': 1,
                    'min_samples_split': 34,
                    'bootstrap': False,
                    'criterion': 'entropy',
                    'n_estimators': 604,
                    'min_samples_leaf': 2,
                    'max_depth': 19,
                    'random_state': 0}

ca_with_registrar = {'max_features': 23,
                     'min_samples_split': 2,
                     'bootstrap': False,
                     'criterion': 'entropy',
                     'n_estimators': 817,
                     'min_samples_leaf': 1,
                     'max_depth': 34,
                     'random_state': 0}

web_host_params = {'max_features': 270,
                   'min_samples_split': 10,
                   'bootstrap': False,
                   'criterion': 'entropy',
                   'n_estimators': 555,
                   'min_samples_leaf': 2,
                   'max_depth': 31,
                   'random_state': 0}

name_features  = ["ft_contains_digit", "ft_contains_hyphen", "ft_length", "ft_novelty_tld", 
                  "ft_contains_news", "ft_newsy_domain", "ft_has_domain_ip"]
whois_features = ["ft_creation_elapsed_time", "ft_time_to_expiration", "ft_time_from_updated", 
                  "ft_whois_lifetime", "ft_domain_proxy", "ft_registrar", "ft_registrant_country", 
                  "ft_registrant_org", "ft_nameserver_sld", "ft_nameserver_ip_info"]
cert_features  = ["ft_domain_validated", "ft_has_expired", "ft_self_signed", "ft_cert_lifetime", 
                  "ft_san_length", "ft_issuer_country", "ft_issuer_org", "ft_san_contains_wildcard", "ft_has_cert"]
html_features  = ["ft_uses_wordpress", "ft_wordpress_themes", "ft_wordpress_plugins", "ft_has_html"]
dns_features   = ["ft_domain_ip_info"]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('training_database_config_file')
    args = parser.parse_args()

    db = DisinfoTrainingDB.init_from_config_file(args.training_database_config_file)

    # Return raw tuples
    raw_training_data = db.query_all()
    desired_features = {"domain": name_features + dns_features,
                        "whois": whois_features,
                        "cert": cert_features,
                        "webpage": html_features}

    d = DisinformationClassifier(raw_training_data, 
                                 desired_features,
                                 save_ft_names=False)
   
    d.classifier.set_params(**full_params)
    d.train() 
    d.save("full_model.pickle")

if __name__ == '__main__':
    main()
