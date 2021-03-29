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


import numpy as np
import pdb
import psycopg2 as pg

from lsengine.pathway_service import PathwayService

class JobRecommendation:

    skill_rank = {'no knowledge':0,
                      'beginner':1,
                      'intermediate':2,
                      'advanced':3,
                      'expert':4}

    def __init__(self, graph, db_url=None, skill_rank=None,
                 multiplier_threshold=1.0, multiplier_baseline=0.0,
                 multiplier_offset=np.sqrt(2), multiplier_power=2,
                 max_skills=5
    ):
        """Initialise with parameters

        skill_rank: Dictionary mapping skill levels to numerical values
        Variables determining how embedding euclidean distances are
            converted to a multiplier on learning rate:
        multiplier_threshold: The maximum distance before the multiplier
            is set to baseline
        multiplier_baseline:  The multiplier used when multiplier reaches
            the threshold (distant skills should contribute little or
            nothing towards learning)
        multiplier_offset:    The minimum point for the learning speed
            conversion
        multiplier_power:     An exponent applied to the learning
            speed conversion
        max_skills:           The maximum number of close skills that modify
            required learning
        """
        self.graph = graph
        self.db_url = db_url
        if skill_rank:
            self.skill_rank = skill_rank
        self.max_skill_gap = (max(self.skill_rank.values())
                              - min(self.skill_rank.values())
        )
        self.multiplier_threshold = multiplier_threshold
        self.multiplier_baseline = multiplier_baseline
        self.multiplier_offset = multiplier_offset
        self.multiplier_power = multiplier_power
        self.max_skills = max_skills


    def job_by_simple_distance(self, source_skills, target_skills):
        """Convert a skill gap to a distance

        The step size from one level of experience to another is
        pre-defined and skills are treated entirely independently"""
        skill_rank = self.skill_rank
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


    def job_by_distance(self, source_skills, target_skills):
        """Convert a skill gap to a distance considering how
        skills are related"""
        all_skills = []
        all_skills.extend(source_skills.keys())
        all_skills.extend(target_skills.keys())
        embeddings = self._get_embeddings(all_skills)
        total_distance = 0
        skills = []
        profile_sum = 0
        for t_id, t_level in target_skills.items():
            profile_sum += self.skill_rank[t_level]
            s_level = source_skills.get(t_id, 'no knowledge')
            skills.append({"id":t_id,
                           "name":self.graph.skills[t_id]["name"],
                           "current_level":s_level,
                           "target_level":t_level,
            })
            tl = self.skill_rank[t_level]
            sl = self.skill_rank[s_level]
            if sl >= tl:
                continue
            all_multipliers = [
                (self._get_learning_speed(embeddings[t_id], embeddings[i]),
                 self.skill_rank[j])
                for i,j in source_skills.items()
                if (t_id != i)
            ]
            all_multipliers.sort(key=lambda x:x[0], reverse=True)
            d = self.skill_rank[t_level] - self.skill_rank[s_level]
            for multiplier,level in all_multipliers[:self.max_skills]:
                level_multiplier = min(tl, level) - min(sl, level)
                level_multiplier /= self.max_skill_gap
                d -= multiplier * d * level_multiplier
            total_distance += d
        if profile_sum == 0:
            fit = 100
        else:
            fit = 100 * (profile_sum - total_distance) / profile_sum
        fit = round(fit, 2)
        total_distance = round(total_distance, 2)
        return {"distance":total_distance,
                "skills":skills,
                "fit":fit,
        }


    def _get_embeddings(self, skill_ids):
        """Fetch embeddings from the database"""
        conn = pg.connect(self.db_url)
        cursor = conn.cursor()
        embeddings = {i:None for i in skill_ids}
        try:
            cursor.execute(
                "SELECT skill_id, use FROM embeddings WHERE skill_id = ANY(%s)",
                [skill_ids]
            )
            embeddings.update({k:np.array(v) for k,v in cursor.fetchall()})
        except:
            conn.rollback()
            raise
        finally:
            conn.close()
        return embeddings


    def _get_learning_speed(self, embed1, embed2):
        """From two embeddings generate a training speed multiplier"""
        if (embed1 is None) or (embed2 is None):
            return self.multiplier_baseline
        d = np.linalg.norm(embed1 - embed2)
        if d > self.multiplier_threshold:
            return self.multiplier_baseline
        y = ((self.multiplier_offset - d)/self.multiplier_offset)
        y = y ** self.multiplier_power
        return y


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
