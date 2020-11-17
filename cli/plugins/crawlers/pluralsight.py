"""Crawler for the Pluralsight platform"""
from io import StringIO
import json
import pandas as pd
import pdb
import requests
import time

from cli.crawlers import GenericCrawler, GenericCrawl, GenericCourse


class PluralsightCourse(GenericCourse):
    parsed = None

    @property
    def to_DB(self):
        """Parse the course for insertion into the database"""
        if not self.parsed:
            self._parse()
        c = self.parsed
        url = 'https://www.pluralsight.com/courses/' + c['CourseId']
        output = {'name':c['CourseTitle'],
                  'type':'course-online',
                  'platform':'Pluralsight',
                  'duration':c['DurationInSeconds'],
                  'url':url,
                  'duration_code':'S',
                  'alt_id':c['CourseId'],
                  'description':c['Description'],
                  'short_description':c['Description'],
                  'weekly_effort':None}
        return output


    @property
    def to_ML(self):
        """Parse the course for use in machine learning"""
        if not self.parsed:
            self._parse()
        content = self.parsed
        return "{CourseTitle} {Description}".format(**content)


    @property
    def is_active(self):
        if not self.parsed:
            self._parse()
        if self.parsed['IsCourseRetired'] == 'no':
            return True
        return False

    def _parse(self):
        self.parsed = json.loads(self.data)



class PluralsightCrawl(GenericCrawl):
    course = PluralsightCourse

    def _crawl(self, resource):
        course_url = "http://api.pluralsight.com/api-v0.9/courses"
        response = requests.get(course_url)
        assert response.status_code == 200
        fp = StringIO(response.content.decode('utf-8'))
        courses = pd.read_csv(fp)
        for i, row in courses.iterrows():
            yield self.course(row.to_json())



class Pluralsight(GenericCrawler):
    name = 'pluralsight'
    crawl = PluralsightCrawl


