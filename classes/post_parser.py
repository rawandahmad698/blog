import os
import json


def get_posts():
    """ Open posts.json under static and return a list of post objects """
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_file_path = os.path.join(parent_dir, 'static', 'posts.json')
    try:
        with open(json_file_path) as f:
            posts = json.load(f)['posts']
            f.close()
            return posts
    except FileNotFoundError:
        print(">> Could not find file: {}".format(json_file_path))
    except Exception as e:
        print(">> Error while parsing file: {}".format(e))