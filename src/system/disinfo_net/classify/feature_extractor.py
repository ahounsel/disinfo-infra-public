import pandas as pd

from disinfo_net.features.whois_features import WhoisFeatures
from disinfo_net.features.certificate_features import CertificateFeatures
from disinfo_net.features.domain_features import DomainFeatures
from disinfo_net.features.webpage_features import WebpageFeatures

class FeatureExtractor:
    
    @staticmethod
    def get_features(resp, desired_features): 
        all_features = []
        for name in desired_features:
            feature_names = desired_features[name]
            if name == 'domain':
                features = DomainFeatures.get_features(feature_names=feature_names,
                                                       raw_data=resp.dns,
                                                       available=True,
                                                       domain=resp.domain)
            elif name == 'whois':
                features = WhoisFeatures.get_features(feature_names=feature_names,
                                                       raw_data=resp.whois,
                                                       available=True,
                                                       domain=resp.domain)
            elif name == 'webpage':
                features = WebpageFeatures.get_features(feature_names=feature_names,
                                                       raw_data=resp.html,
                                                       available=True,
                                                       domain=resp.domain)
            elif name == 'cert':
                features = CertificateFeatures.get_features(feature_names=feature_names,
                                                            raw_data=resp.certificate,
                                                            available=True,
                                                            domain=resp.domain)
            else:
                features = pd.DataFrame(index=resp.domain)
            all_features.append(features)

        df = pd.concat(all_features, axis=1)
        return df
