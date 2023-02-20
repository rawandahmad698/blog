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

test_mode = False

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    # posts = p.get_posts() # Local
    # print("Posts: {}".format(posts))
    if not test_mode:
        posts = await p.get_posts_from_aws()  # AWS
    else:
        posts = p.get_posts()  # Local

    posts = sorted(posts, key=lambda k: k['id'], reverse=True)
    context = {'request': request, 'posts': posts}
    print("Context: {}".format(context))
    return templates.TemplateResponse("index.html", context)


@app.get("/post", response_class=HTMLResponse)
async def read_item(request: Request, pid: str):
    if pid is None:
        posts = await p.get_posts_from_aws()  # AWS
        return templates.TemplateResponse("index.html", {"request": request, "posts": posts})

    if not test_mode:
        post_data = await pp.parse_paragraphs_aws(f"{pid}.yml")  # AWS
        if post_data is None:
            posts = await p.get_posts_from_aws()  # AWS
            return templates.TemplateResponse("index.html", {"request": request, "posts": posts})
    else:
        post_data = pp.parse_paragraphs(f"{pid}.yml") # Local

    title = post_data['title']
    description = post_data['description']
    image = post_data['image']
    timestamp = post_data['timestamp']
    locale = post_data['locale']
    direction = post_data['dir']

    await u.increment_post_views(pid)

    view_count = await u.get_post_views(pid)
    if locale != "en":
        view_count = u.num_to_ar(view_count)

    post = {
        'title': title,
        'description': description,
        'image': image,
        'view_count': view_count,
        'timestamp': timestamp,
        "locale": locale,
        "dir": direction
    }
    context = {"request": request, 'paragraph_list': post_data['paragraphs'], 'links': post_data['links'],
               'post': post}
    print("Context: {}".format(context))
    return templates.TemplateResponse("view_post.html", context)
