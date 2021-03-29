from collections import defaultdict
import tensorflow as tf
import tensorflow_hub as hub
from psycopg2.extras import Json

from .config import Config
from .classifiers import get_skills

tf.get_logger().setLevel('ERROR')

module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
embed = hub.load(module_url)

def process(x):
    message_embeddings = embed(x)
    return message_embeddings


def generate_skill_embeddings(organisations, glue=", "):
    """Generate USE embeddings for skill paths"""
    # Gather all skill paths
    db = Config.get_db_cursor()
    organisations = organisations.split(",")
    skill_paths = defaultdict(list)
    skill_ids = []
    for organisation in organisations:
        skills = get_skills(organisation)
        for skill in skills:
            skill_paths[glue.join([i["name"] for i in skill])].append(
                skill[-1]["id"]
            )
            skill_ids.append(skill[-1]["id"])
    # Generate embeddings
    sp = list(skill_paths.keys())
    embeddings = {k:v.numpy().tolist() for k,v in zip(sp, process(sp))}
    # Get old embeddings
    db.execute("SELECT skill_id FROM embeddings WHERE skill_id = ANY(%s)",
               [skill_ids])
    old_ids = [i[0] for i in db.fetchall()]
    # Insert embeddings
    for sp, s_ids in skill_paths.items():
        for s_id in s_ids:
            if s_id in old_ids:
                # Update
                db.execute(
                    "UPDATE embeddings SET use = %s WHERE skill_id = %s",
                    [Json(embeddings[sp]), s_id]
                )
            else:
                #Insert new
                db.execute(
                    "INSERT INTO embeddings (skill_id, use) VALUES (%s, %s)",
                    [s_id, Json(embeddings[sp])]
                )
    Config.db_conn.commit()
    print("Embeddings successfully created", flush=True)


