#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml

class Config():
    """The configuration stored in a config file"""
    def __init__(self, configfile):
        self.configfile = configfile
        self.set_default()
        self.read_options()

    def set_default(self):
        """Initialize with default values"""
        self.options = {
            'projects' : ['/data/Dropbox/programming/EP_report2/ep_report'],
            'default_project' : 0
            }
        

    def read_options(self):
        try:
            yaml.load(self.configfile)
            for key in self.options:
                self.options[key] = self.parser.get('options', key)

        except: # if file is not present or is damaged
            self.write_options() # write a new file
            return # donot change defaults
            
        print self.options


    def write_options(self):
        with open(self.configfile, 'w') as fi:
            yaml.dump(self.options, fi)

