# Builtins
import asyncio

# Database
import motor.motor_asyncio

# DB Info
database_client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
database_client.get_io_loop = asyncio.get_running_loop

post_stats = database_client['PostStats']


async def get_post_views(pid: str) -> int:
    post = await post_stats.posts.find({'pid': pid}).to_list(length=1)
    if len(post) == 0:
        return 0

    return post[0]['views']


async def increment_post_views(pid: str):
    post = await post_stats.posts.find({'pid': pid}).to_list(length=1)
    if len(post) == 0:
        # Create the post
        await post_stats.posts.insert_one({'pid': pid, 'views': 1})
    else:
        await post_stats.posts.update_one({'pid': pid}, {'$inc': {'views': 1}})
        # print(f"Updated {x.modified_count} document(s).")


def num_to_ar(num: int) -> str:
    arabic_numbers = {
        '0': '٠',
        '1': '١',
        '2': '٢',
        '3': '٣',
        '4': '٤',
        '5': '٥',
        '6': '٦',
        '7': '٧',
        '8': '٨',
        '9': '٩'
    }
    return ''.join([arabic_numbers.get(c, c) for c in str(num)])
