# FastAPI
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Local
from classes import paragraph_parser as pp
from classes import utils as u
from classes import post_parser as p

# Create the app
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    # posts = p.get_posts() # Local
    posts = await p.get_posts_from_aws()  # AWS
    context = {'request': request, 'posts': posts}
    return templates.TemplateResponse("index.html", context)


@app.get("/post", response_class=HTMLResponse)
async def read_item(request: Request, pid: str):
    if pid is None:
        posts = await p.get_posts_from_aws()  # AWS
        return templates.TemplateResponse("index.html", {"request": request, "posts": posts})

    # post_data = pp.parse_paragraphs(f"{pid}.yml") # Local
    post_data = await pp.parse_paragraphs_aws(f"{pid}.yml")  # AWS
    if post_data is None:
        posts = await p.get_posts_from_aws()  # AWS
        return templates.TemplateResponse("index.html", {"request": request, "posts": posts})

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
