# Copyright (C) 2021  Learnershape and contributors

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

from celery import shared_task
from collections import defaultdict
import pdb

from lsgraph import models
from lsgraph.models import db


def get_descendant_skills(skill_id):
    """Get all skills that originate from skill_id"""
    if not isinstance(skill_id, (list, tuple)):
        skill_id = [
            skill_id,
        ]
    topq = db.session.query(models.SkillInclude).filter(
        models.SkillInclude.parent_id.in_(skill_id)
    )
    topq = topq.cte("cte", recursive=True)
    bottomq = db.session.query(models.SkillInclude)
    bottomq = bottomq.join(topq, models.SkillInclude.parent_id == topq.c.child_id)
    recursive_q = topq.union(bottomq)
    final_q = db.session.query(recursive_q)
    children = defaultdict(list)
    for _, parent, child in final_q.all():
        children[parent].append(child)
    descendants = defaultdict(list)

    def collect_descendants(skill_id, children):
        output = []
        if skill_id not in children:
            return output
        output.extend(children[skill_id])
        for s_id in children[skill_id]:
            output.extend(collect_descendants(s_id, children))
        return output

    all_descendants = {s_id: collect_descendants(s_id, children) for s_id in skill_id}
    direct_children = {k: v for k, v in children.items() if k in skill_id}
    return all_descendants, direct_children


def get_ancestor_skills(skill_id):
    """Get all skills connecting root_id to skill_id"""
    if not isinstance(skill_id, (list, tuple)):
        skill_id = [
            skill_id,
        ]
    topq = db.session.query(models.SkillInclude).filter(
        models.SkillInclude.child_id.in_(skill_id)
    )
    topq = topq.cte("cte", recursive=True)
    bottomq = db.session.query(models.SkillInclude)
    bottomq = bottomq.join(topq, models.SkillInclude.child_id == topq.c.parent_id)
    recursive_q = topq.union(bottomq)
    final_q = db.session.query(recursive_q)
    parents = {child: parent for _, parent, child in final_q.all()}
    output = defaultdict(list)

    def build_path(output, skill_id, parents):
        extended = False
        for s_id in skill_id:
            if s_id in output:
                current = output[s_id][-1]
            else:
                current = s_id
            if current in parents:
                extended = True
                output[s_id].append(parents[current])
        if extended:
            build_path(output, skill_id, parents)

    build_path(output, skill_id, parents)
    return output


def get_root_id(skill_id):
    """Get the root IDs for a collection of skills"""
    output = get_ancestor_skills(skill_id)
    output = {k: v[-1] for k, v in output.items()}
    return output


module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"


class SkillProcessor:
    embed = None

    @classmethod
    def process(cls, x):
        if not cls.embed:
            import tensorflow_hub

            cls.embed = tensorflow_hub.load(module_url)
        message_embeddings = cls.embed(x)
        return message_embeddings


@shared_task
def skill_embedding(skill_id):
    """Generate a new skill embedding"""
    # Get full path for skill
    ancestors = get_ancestor_skills(skill_id)[skill_id]
    skill_chain = [
        skill_id,
    ]
    skill_chain.extend(ancestors[:-1])
    all_skills = models.Skill.query.filter(models.Skill.id.in_(skill_chain)).all()
    all_skills = {i.id: i for i in all_skills}
    skill_path = ", ".join([all_skills[i].name for i in reversed(skill_chain)])
    # Compute embedding for skill path
    vector = SkillProcessor.process(
        [
            skill_path,
        ]
    )
    vector = vector.numpy()[0].tolist()
    # Store embedding in database
    all_skills[skill_id].skill_embedding = vector
    db.session.add(all_skills[skill_id])
    db.session.commit()
