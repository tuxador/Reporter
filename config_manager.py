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
            'default_project' : 0,    
            'backup_freq': 1,
            'num_backups':5,
            }
        

    def read_options(self):
        try:
            with open(self.configfile) as fi:
                self.options = yaml.load(fi)
        except: # if file is not present or is damaged
            print "didn't work"
            self.write_options() # write a new file
            return # donot change defaults
            

    def write_options(self):
        with open(self.configfile, 'w') as fi:
            yaml.dump(self.options, fi)

