import click
from copy import deepcopy
import json
import os
import psycopg2 as pg
import sys


class Config:
    c = {}
    plugin_directory = ['cli/plugins']
    active = {}
    db_conn = None

    @classmethod
    def load(cls, config):
        """Load config from best source

        CLI (highest priority), environment variable,
        default (lowest priority)
        """
        if config:
            config_file = config
            msg = 'command line'
        elif 'LS_PIPELINE_CONFIG' in os.environ:
            config_file = os.environ['LS_PIPELINE_CONFIG']
            msg = 'environment variable'
        else:
            config_file = 'cli/config.json'
            msg = 'default'

        try:
            with open(config_file) as fp:
                data = json.load(fp)
                cls.parse(cls, data)
                return
        except:
            click.echo('Could not parse config file from {0}: {1}'.format(
                msg, config_file)
            )
            sys.exit()


    def parse(cls, data):
        """Parse config to expand environments"""
        assert isinstance(data, dict), "Unexpected config format"
        cls.plugin_directory.extend(data['plugin_directory'])
        envs = data['environments'].keys()
        for e in envs:
            cls.c[e] = cls._parse(cls, data['environments'], e)


    def _parse(cls, data, e):
        """Resolve inheritance in config"""
        if 'inherit_from' in data[e]:
            head = deepcopy(cls._parse(cls, data, data[e]['inherit_from']))
            tail = update_dict(head, data[e])
            return tail
        else:
            return data[e]


    @classmethod
    def set_env(cls, env):
        """Configure the active environment"""
        cls.active = cls.c[env]


    @classmethod
    def get_db_cursor(cls):
        if cls.db_conn == None:
            cls.db_conn = pg.connect(cls.active['db'])
        return cls.db_conn.cursor()



def update_dict(d,n):
    """Merge a default set of constraints with new constraints"""
    for k,v in d.items():
        if k in n:
            if isinstance(v, dict):
                d[k] = update_dict(v,n[k])
            else:
                d[k] = n[k]
    return d
