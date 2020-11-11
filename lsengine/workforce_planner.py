# Copyright (C) 2019-2020  Learnershape and contributors

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

class WorkforcePlanner:
    """Optimize upskilling opportunities across a workforce"""


    def __init__(self, job_rec, targets_per_employee):
        """Set initialization values for planning

        job_rec: JobRecommendation instance
        employees_per_target:
        targets_per_employee:"""
        self.job_rec = job_rec
        self.targets_per_employee = targets_per_employee
        self.employees = []
        self.targets = []


    def add_employee(self, identifier, skills):
        self.employees.append({'id':identifier,
                               'skills':skills})


    def add_target(self, identifier, skills, number_needed, max_training):
        self.targets.append({'id':identifier,
                             'skills':skills,
                             'num':number_needed,
                             'max':max_training})


    def plan(self):
        """Plan best target profiles for each employee"""
        distances = []
        employee_options = [0 for _ in range(len(self.employees))]
        target_options = [0 for _ in range(len(self.targets))]
        # Get distances
        for e_idx, e in enumerate(self.employees):
            for t_idx, t in enumerate(self.targets):
                d = self.job_rec.job_by_distance(e['skills'],
                                                 t['skills'])['distance']
                if d > t['max']:
                    continue
                distances.append((e_idx, t_idx, d))
                employee_options[e_idx] += 1
                target_options[t_idx] += 1
        distances.sort(key=lambda x:x[2], reverse=True)
        # Prune connections
        preserved_distances = []
        for d in distances:
            if (employee_options[d[0]] > self.targets_per_employee) and \
               (target_options[d[1]] > self.targets[d[1]]['num']):
                employee_options[d[0]] -= 1
                target_options[d[1]] -= 1
                continue
            preserved_distances.append(d)
        # Build results
        employee_targets = {i['id']:[] for i in self.employees}
        target_employees = {i['id']:[] for i in self.targets}
        for e_idx, t_idx, d in preserved_distances:
            e_id = self.employees[e_idx]['id']
            t_id = self.targets[t_idx]['id']
            employee_targets[e_id].append((t_id, d))
            target_employees[t_id].append((e_id, d))
        for i in employee_targets.values():
            i.sort(key=lambda x:x[1])
        for i in target_employees.values():
            i.sort(key=lambda x:x[1])
        target_level_map = {i['id']:total_levels(i['skills']) for i \
                            in self.targets}

        def percent_e(profiles):
            r = []
            for t_id,d in profiles:
                l = target_level_map[t_id]
                pc = 100 * (l - d) / l
                r.append((t_id, round(pc, 2)))
            return r

        def percent_t(profiles, levels):
            r = []
            for p_id,d in profiles:
                pc = 100 * (levels - d) / levels
                r.append((p_id, round(pc, 2)))
            return r

        employee_targets = {k:percent_e(v[:self.targets_per_employee]) \
                            for k,v in employee_targets.items()}
        target_map = {i['id']:i['num'] for i in self.targets}
        target_employees = {k:percent_t(v[:target_map[k]],
                                      target_level_map[k]) for k,v in \
                            target_employees.items()}
        return {'targets_by_employee':employee_targets,
                'employees_by_target':target_employees}


def total_levels(skills):
    skill_rank = {'no knowledge':0,
                      'beginner':1,
                      'intermediate':2,
                      'advanced':3,
                      'expert':4}
    t = 0
    for skill_id,level in skills.items():
        t += skill_rank[level]
    return t
