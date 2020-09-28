import pandas as pd
import numpy as np
import datetime
import csv
from bs4 import BeautifulSoup

from disinfo_net.postgres.pg import DisinfoRawDataDB
from disinfo_net.util.html_util.wordpress_info import WordpressInfo

class WebpageFeatures():
   
    wordpress_info = WordpressInfo()

    @staticmethod
    def get_feature_names():
        global_info = globals()["WebpageFeatures"]
        members = dir(global_info)
        feature_names = []
        for member in members:
            if "ft_" in member:
                feature_names += [member]
        return feature_names

    @staticmethod
    def get_features(feature_names, raw_data, available, domain):
        # Get features from the HTML source 
        features = {}
        to_concat = []
        for feature_name in feature_names:
            module = globals()["WebpageFeatures"]
            feature_func = getattr(module, feature_name)
            kwargs = {"raw_data": raw_data, "available": available, "domain": domain}
            val = feature_func(**kwargs)
            if isinstance(val, pd.DataFrame):
                to_concat += [val]
            else:
                feature_name = feature_name.replace("ft_", "")
                feature_name = feature_name.replace("_", " ")
                features[feature_name] = val
        df = pd.DataFrame(index=[domain], data=features)
        to_concat += [df]
        df = pd.concat(to_concat, axis=1)
        return df

    @staticmethod
    def ft_has_html (raw_data=None, available=False, domain=""):
        if pd.isna(raw_data):
            return "False"
        return "True"

    @staticmethod
    def ft_uses_wordpress(raw_data=None, available=False, domain=""):
        if pd.isna(raw_data):
            return "N/A"

        try:
            soup = BeautifulSoup(raw_data, 'html.parser')
        except Exception as e:
            return "False"

        wp_src = soup.find_all(lambda tag: tag.has_attr('src') and 'wp-content' in tag['src'])
        wp_href = soup.find_all(lambda tag: tag.has_attr('href') and 'wp-content' in tag['href'])
        if len(wp_src) > 0 or len(wp_href) > 0:
            return "True"
        return "False"

    @staticmethod
    def ft_wordpress_themes (raw_data=None, available=False, domain=""):
        columns = ["ft_wordpress_themes_" + theme 
                   for theme in WebpageFeatures.wordpress_info.themes]
        themes_df = pd.DataFrame(index=[domain], columns=columns, dtype=np.bool)
        
        if pd.isna(raw_data):
            themes_df[columns] = "N/A"
            return themes_df
        else:
            themes_df[columns] = "False"

        for t in WebpageFeatures.wordpress_info.themes:
            if raw_data and raw_data.find("themes/" + t) != -1:
                themes_df["ft_wordpress_themes_" + t] = "True"
        return themes_df        

    @staticmethod
    def ft_wordpress_plugins (raw_data=None, available=False, domain=""):
        columns = ["ft_wordpress_plugins_" + plugin 
                   for plugin in WebpageFeatures.wordpress_info.plugins]
        plugins_df = pd.DataFrame(index=[domain], columns=columns, dtype=np.bool)

        if pd.isna(raw_data):
            plugins_df[columns] = "N/A"
            return plugins_df
        else:
            plugins_df[columns] = "False"

        for p in WebpageFeatures.wordpress_info.plugins:
            if raw_data and raw_data.find("plugins/" + p) != -1:
                plugins_df["ft_wordpress_plugins_" + p] = "True"
        return plugins_df
