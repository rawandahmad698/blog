import os
import json
import aiohttp


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


async def get_posts_from_aws() -> list:
    url = "https://s3.me-south-1.amazonaws.com/rawa.dev-blog/posts.json"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    posts = await resp.text()
                    posts = json.loads(posts)
                    return posts['posts']
                else:
                    print(">> Error while fetching posts from AWS")
                    return []
    except Exception as e:
        print(">> Error while getting posts from AWS: {}".format(e))
        return []
    finally:
        await session.close()
