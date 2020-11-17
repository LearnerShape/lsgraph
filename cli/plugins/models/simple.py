from bs4 import BeautifulSoup
import click
from fuzzywuzzy import fuzz
from joblib import load
import json
import os
import pandas as pd
import pdb
from zipfile import ZipFile

from cli.classifiers import GenericClassifier


def clean_text(text):
    if text is None:
        return ''
    soup = BeautifulSoup(text, 'lxml')
    clean = soup.get_text()
    for i,j in [('\n', ' '), ('\xa0', ' ')]:
        clean = clean.replace(i,j)
    return clean.lower()


class Simple(GenericClassifier):
    name = 'simple'

    def run(self):
        """Run a model on a set of skills and courses"""
        click.echo([str(i) for i in self.crawlers])
        if self.status == 'COMPLETE':
            click.echo('Classifier has already been run')
            return
        model_dir = os.path.split(__file__)[0]
        rf_fn = os.path.join(model_dir, 'classifier_RF_20201028.joblib')
        lr_fn = os.path.join(model_dir, 'classifier_LR_20201028.joblib')
        ab_fn = os.path.join(model_dir, 'classifier_AB_20201028.joblib')
        rf_clf = load(rf_fn)
        lr_clf = load(lr_fn)
        ab_clf = load(ab_fn)
        all_paths_no_leaf = ["|".join(i.split('|')[:-1]) for i in self.skills]
        all_paths_no_leaf = set(all_paths_no_leaf)
        output_i = 0
        output = {}
        with ZipFile(os.path.join(self.results_dir, self.fn), 'a') as z:
            for crawler in self.crawlers:
                crawler_name = crawler.crawler.name
                for identifier, h_id in crawler.list_courses().items():
                    course = crawler.get_course(h_id).to_DB
                    course['name'] = clean_text(course['name'])
                    course['description'] = clean_text(course['description'])
                    X = []
                    for skill_path in self.skills:
                        course_features = self._extract_course_features(
                            course, skill_path,
                            all_paths_no_leaf,
                        )
                        X.append(course_features)
                    X = pd.DataFrame(X)
                    rf_prob = rf_clf.predict_proba(X)
                    lr_prob = lr_clf.predict_proba(X)
                    ab_prob = ab_clf.predict_proba(X)
                    course_identifier = "{0}|{1}".format(crawler_name, h_id)
                    output[course_identifier] = {'RF':rf_prob[:,1].tolist(),
                                                 'LR':lr_prob[:,1].tolist(),
                                                 'AB':ab_prob[:,1].tolist()}
                    if len(output) % 50 == 0:
                        click.echo('.')
                    if len(output) >= 1000:
                        output, output_i = self._save_data(z, output,
                                                           output_i)
            output, output_i =  self._save_data(z, output, output_i)
            with z.open('status', 'w') as fp:
                fp.write('COMPLETE'.encode('utf-8'))
                self.status = 'COMPLETE'


    def courses_for_skill(self, skill):
        """Get a filtered list of courses for a skill"""
        skill_id = self.skills.index(skill)
        with ZipFile(os.path.join(self.results_dir, self.fn), 'a') as z:
            files = z.namelist()
            files = [i for i in files if i.startswith('scores_')]
            for fn in files:
                with z.open(fn) as fp:
                    data = json.loads(fp.read())
                    for k,v in data.items():
                        scores = [v['RF'][skill_id],
                                  v['LR'][skill_id],
                                  v['AB'][skill_id]]
                        if any([i > 0.5 for i in scores]):
                            yield (k, scores)


    def list_courses(self):
        """Get all courses"""
        self.idx = {}
        with ZipFile(os.path.join(self.results_dir, self.fn)) as z:
            files = z.namelist()
            files = [i for i in files if i.startswith('scores_')]
            for fn in files:
                with z.open(fn) as fp:
                    data = json.loads(fp.read())
                    for k in data.keys():
                        self.idx[k] = fn
                        yield k


    def skills_for_course(self, course):
        """Get matching skills for a course"""
        if not hasattr(self, idx):
            for i in self.list_courses():
                pass
        fn = self.idx.get(course, None)
        if not fn:
            return []
        with ZipFile(os.path.join(self.results_dir, self.fn)) as z:
            with z.open(fn) as fp:
                data = json.loads(fp.read())
            output = data[course]
        for s,rf,lr,ab in zip(self.skills, output['RF'],
                              output['LR'], output['AB']):
            scores = [rf,lr,ab]
            if any([i>0.5 for i in scores]):
                yield (s, scores)


    def _save_data(self, resource, output, output_i):
        if not output:
            return output, output_i
        output_fn = "scores_{0:05}.json".format(output_i)
        with resource.open(output_fn, 'w') as fp:
            fp.write(json.dumps(output).encode('utf-8'))
        output = {}
        output_i += 1
        click.echo('Writing results to {0}'.format(output_fn))
        return output, output_i


    def _extract_course_features(self, course, skill_path, all_paths_no_leaf):
        skill_name = skill_path.split('|')[-1].lower()
        name = course['name']
        description = course['description']
        fuzz_name = fuzz.partial_ratio(skill_name, name)
        fuzz_description = fuzz.partial_ratio(skill_name, description)
        return {'name_length':len(name) if name else 0,
                'description_length':len(description) if description else 0,
                'platform':course['platform'],
                'skill_in_name':skill_name in name,
                'skill_in_description':False if not description else skill_name in description,
                'fuzz_name':fuzz_name,
                'fuzz_description':fuzz_description,
                'leaf_node':skill_path in all_paths_no_leaf,
        }
