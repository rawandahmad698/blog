# Builtins
import asyncio
import os
import signal
import sys

# Env
from dotenv import load_dotenv

# Sockets
import websockets

# FastAPI
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Local
from classes import paragraph_parser as pp
from classes import utils as u
from classes import post_parser as p
from shlex import quote as shlex_quote

load_dotenv()

# First, get environment variables
github_api_token = os.getenv("GITHUB_API_TOKEN")
github_repo = os.getenv("GITHUB_REPO")
socket_address = os.getenv("SOCKET_ADDRESS")


# If any of the environment variables are missing, exit
if github_api_token is None or github_repo is None or socket_address is None:
    print(">> Missing environment variables. Exiting...")
    print(">> github_api_token:", github_api_token)
    print(">> github_repo:", github_repo)
    print(">> socket_address:", socket_address)
    sys.exit()

# Create the app
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    posts = p.get_posts()
    print(posts)
    context = {'request': request, 'posts': posts}
    return templates.TemplateResponse("index.html", context)


@app.get("/post", response_class=HTMLResponse)
async def read_item(request: Request, pid: str):
    if pid is None:
        return templates.TemplateResponse("index.html", {"request": request})

    post_data = pp.parse_paragraphs(f"{pid}.yml")

    print("Links: {}".format(post_data))
    title = post_data['title']
    description = post_data['description']
    image = post_data['image']
    timestamp = post_data['timestamp']

    await u.increment_post_views(pid)

    view_count = await u.get_post_views(pid)
    view_count = u.num_to_ar(view_count)

    post = {
        'title': title,
        'description': description,
        'image': image,
        'view_count': view_count,
        'timestamp': timestamp,
    }
    context = {"request": request, 'paragraph_list': post_data['paragraphs'], 'links': post_data['links'],
               'post': post}
    return templates.TemplateResponse("view_post.html", context)


async def update(ws):
    await ws.close()

    os.system(f"meshsync -u -f -t {github_api_token} -o {github_repo}")
    await asyncio.sleep(3)
    stop_command = "sudo systemctl stop fastapi_demo"
    os.system(stop_command)

    await asyncio.sleep(1)

    start_command = "sudo systemctl start fastapi_demo"
    os.system(start_command)
    await asyncio.sleep(1)

    sys.exit()  # Exit current script


async def socket_handler():
    try:
        params = "Blog-FastAPI"
        async with websockets.connect(f"{socket_address}{params}",
                                      ping_interval=1) \
                as websocket:
            print(">> Connected to websocket")
            while True:
                await websocket.ping()

                message = await websocket.recv()
                print(f">> Received: {message}")
                if 'update' in message:
                    await update(websocket)
                    await asyncio.sleep(1)
                    print(">> Script updated")
                    os.kill(os.getpid(), signal.SIGTERM)
                    sys.exit()

                await asyncio.sleep(1)

    except Exception as e:
        print("Error in socket_handler:", e)
        await socket_handler()


async def background_task():
    await socket_handler()


@app.on_event("startup")
async def startup_event():
    try:
        asyncio.create_task(background_task())
    except asyncio.CancelledError:
        print("Task cancelled")
        os.kill(os.getpid(), signal.SIGTERM)
        sys.exit()
