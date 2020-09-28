import os
import sys
import pkg_resources

WP_THEMES = "wp_themes.txt"
WP_PLUGINS = "wp_plugins.txt"

class WordpressInfo:
    def __init__(self):
        resource_package = __name__  
        tf = pkg_resources.resource_filename(resource_package, '/{0}'.format(WP_THEMES))
        self.themes = self.load_themes(tf)
        pf = pkg_resources.resource_filename(resource_package, '/{0}'.format(WP_PLUGINS))
        self.plugins = self.load_plugins(pf)        

    def load_themes(self, themes_filename):
        with open (themes_filename, "r") as f:
            themes = list(set(f.read().splitlines()))
        return themes

    def load_plugins(self, plugins_filename):
        with open (plugins_filename, "r") as f:
            plugins = list(set(f.read().splitlines()))
        return plugins        
