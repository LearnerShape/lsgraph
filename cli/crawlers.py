"""Registers all crawlers in the plugin directories"""
from bs4 import BeautifulSoup
import click
from datetime import datetime
import hashlib
import json
import importlib
import os
import sys
import time
from zipfile import ZipFile

from .config import Config

class Crawlers:
    crawlers = {}


    @classmethod
    def load(cls, plugin_directories):
        """Load all crawlers from the plugin directories"""
        for plugin_directory in plugin_directories:
            cls._load(cls, os.path.join(plugin_directory, 'crawlers'))


    def _load(cls, plugin_directory):
        """Find and load all crawlers in one directory"""
        f = os.listdir(plugin_directory)
        f = [i for i in f if i.endswith('.py')]
        # Convert names
        def convert_names(s):
            s = s[:-3]
            return (s, ''.join([i[0].upper() + i[1:] for i in s.split('_')]))
        f = [convert_names(i) for i in f]
        # Change path
        current_path = sys.path[:]
        sys.path = [plugin_directory] + current_path

        # Load modules
        for mod,c in f:
            crawler = importlib.import_module(mod).__getattribute__(c)
            cls.crawlers[mod] = crawler

        # Change path back
        sys.path = current_path



def begin_crawl(organisation, provider):
    """Collect provider to crawl and begin"""
    assert (organisation and not provider) or (provider and not organisation)
    collected_providers = []
    if organisation:
        p = Config.active['organisations'][organisation]['providers']
        collected_providers = p
    if provider:
        collected_providers = provider.split(',')
    for p in collected_providers:
        c = Crawlers.crawlers[p](Config.active['results_dir'])
        identifier = c.start()
        click.echo(identifier)



class GenericCrawler:
    def __init__(self, results_dir):
        self.results_dir = results_dir


    def start(self):
        """Initialise new crawl"""
        c = self.crawl(self)
        return c.identifier


    def list(self):
        """List all crawls associated with this provider"""
        files = os.listdir(self.results_dir)
        files = [i[:-4] for i in files if i.startswith(self.prefix) and \
                 i.endswith('.zip')]
        files.sort()
        return files


    def get_crawl(self, identifier):
        """Get a specific crawl"""
        return self.crawl(self, identifier)


    @property
    def prefix(self):
        return "crawl_{0}_".format(self.name)



class GenericCrawl:
    def __init__(self, crawler, identifier=None):
        """Initialize a new crawl of the provider"""
        self.crawler = crawler
        self.results_dir = self.crawler.results_dir
        if identifier:
            self.fn = "{0}.zip".format(identifier)
            self.identifier = identifier
            with ZipFile(os.path.join(self.results_dir, self.fn)) as z:
                if "index.json" in z.namelist():
                    with z.open('index.json') as fp:
                        idx = json.loads(fp.read())
                        self.idx = idx
                else:
                    self._build_index()
        else:
            dt = datetime.now().strftime("%Y%m%d%H%M%S")
            identifier = "{0}{1}".format(self.crawler.prefix, dt)
            self.identifier = identifier
            self.fn = "{0}.zip".format(identifier)
            self.start_crawl()


    def start_crawl(self):
        """Start a new crawl"""
        idx = {}
        with ZipFile(os.path.join(self.results_dir, self.fn), 'x') as z:
            for c in self._crawl(z):
                if c.identifier in idx:
                    click.echo("Duplicate record")
                    click.echo(str(identifier))
                    continue
                identifier, fn = c.save(z)
                idx[identifier] = fn
            with z.open('index.json', 'w') as fp:
                fp.write(json.dumps(idx).encode('utf-8'))
        self.idx = idx


    def _build_index(self):
        idx = {}
        with ZipFile(os.path.join(self.results_dir, self.fn), 'a') as z:
            files = z.namelist()
            for f in files:
                if f == "index.json":
                    continue
                course = self.get_course(f)
                idx[course.identifier] = f
            with z.open('index.json', 'w') as fp:
                fp.write(json.dumps(idx).encode('utf-8'))
        self.idx = idx


    def _crawl(self, resource):
        """Provider specific crawling logic"""
        raise Exception("Not Implemented")


    def get_courses(self):
        """Get all courses found in this crawl"""
        with ZipFile(os.path.join(self.results_dir, self.fn)) as z:
            for identifier,fn in self.idx.items():
                yield self.course.load_file(z, fn)


    def get_course_number(self):
        """Get total number of courses found in this crawl"""
        return len(self.idx)


    def list_courses(self):
        """List all courses"""
        return self.idx


    def get_course(self, identifier):
        """Get a specific course"""
        with ZipFile(os.path.join(self.results_dir, self.fn)) as z:
            return self.course.load_file(z, identifier)



class GenericCourse:

    def __init__(self, data, load_time=0):
        """Initialize with data pulled from provider"""
        self.data = data
        self.load_time = load_time
        t_start = time.time()
        self.identifier = self.to_DB['alt_id']
        t_end = time.time()
        self.parse_time = t_end-t_start


    @classmethod
    def load_file(cls, resource, fn):
        """Initialize with data pulled from a file"""
        t_start = time.time()
        with resource.open(fn) as fp:
            data = fp.read()
        t_end = time.time()
        return cls(data, t_end-t_start)


    def save(self, resource):
        """Save course to the crawl archive"""
        fn = h(self.identifier)
        with resource.open(fn, 'w') as fp:
            fp.write(self.data.encode('utf-8'))
        return (self.identifier, fn)


    @property
    def to_DB(self):
        """Parse the course for insertion into the database"""
        raise Exception('Not Implemented')


    @property
    def to_ML(self):
        """Parse the course for use in the """
        raise Exception('Not implemented')


    @property
    def is_active(self):
        return True


def h(identifier):
    """Hash an identifier to something safe to use as a filename"""
    return hashlib.sha1(identifier.encode('utf-8')).hexdigest()




def clean(x):
  if x is None:
    return ''
  soup = BeautifulSoup(x, 'lxml')
  text = soup.get_text()
  text = text.replace('\n',' ')
  return text



def clean_text(t):
    if not t:
        return ''
    to_remove = ['&nbsp;', '•', '\r', "\xa0"]
    for c in to_remove:
        t = t.replace(c, ' ')
    return clean(t)

