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

from lsengine.pathway_service import PathwayService
import numpy as np



class JobRecommendation:

    def __init__(self, graph):
        self.graph = graph


    def job_by_distance(self, source_skills, target_skills):
        """Convert a skill gap to a distance

        The step size from one level of experience to another is
        pre-defined and skills are treated entirely independently"""
        skill_rank = {'no knowledge':0,
                      'beginner':1,
                      'intermediate':2,
                      'advanced':3,
                      'expert':4}
        d = 0
        skills = []
        for s,l in target_skills.items():
            if l is None:
              tl = 2
            else:
              tl = skill_rank[l]
            sl = skill_rank[source_skills.get(s, 'no knowledge')]
            l_diff = tl - sl
            d += l_diff if l_diff > 0 else 0
            skills.append({"id":s,
                           "name":self.graph.skills[s]["name"],
                           "current_level":source_skills.get(s,
                                                             "no knowledge"),
                           "target_level":l})
        return {"distance":d, "skills":skills}


    def job_by_duration(self, source_skills, target_skills,
                                 return_options = False):
        """Convert a skill gap to a duration based on how long
        recommended courses would take to complete

        The step size depends on the course length and does not depend
        on the level difference for a skill. It is also possible for
        one course to teach multiple skills"""
        constraints = {'time':{'target_weekly_effort':5,
                       'maximum_weekly_effort':10,
                       'target_duration':12,
                       'maximum_duration':104}}
        def prune_schedule(schedule):
            while len(schedule) and schedule[-1] == {}:
                schedule.pop()
            return schedule

        PS = PathwayService(self.graph,
                      source_skills,
                      target_skills,
                      constraints)
        PS.identify_skill_gap()
        PS.get_skill_scores()
        options = PS._get_candidate_course_selections(n=1000)
        max_hours_per_week = constraints['time']['maximum_weekly_effort']
        weeks_to_plan = constraints['time']['maximum_duration']
        duration = []
        for best, course_skills in options:
            schedule = PS._schedule_courses(best,
                            max_hours_per_week=max_hours_per_week,
                            weeks_to_plan=weeks_to_plan)
            schedule = prune_schedule(schedule)
            duration.append(len(schedule))
        median_duration = np.median(duration)
        skills = self.job_by_distance(source_skills, target_skills)["skills"]
        to_return = {"distance":median_duration,
                     "skills":skills}
        if return_options:
            to_return["duration_details"] = duration
        return to_return


    def multiple_jobs_by_distance(self, source_skills, target_skills):
        """Evaluate distance for multiple target skill profiles"""
        results = []
        for ts in target_skills:
            results.append(self.job_by_distance(source_skills, ts))
        return results


    def multiple_jobs_by_duration(self, source_skills, target_skills):
        """Evaluate distance for multiple target skill profiles"""
        results = []
        for ts in target_skills:
            results.append(self.job_by_duration(source_skills, ts))
        return results
