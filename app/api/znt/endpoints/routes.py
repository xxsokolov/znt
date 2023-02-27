from fastapi import APIRouter
from typing import List
from app.api.znt.config import database
import secrets

from app.api.znt.models import posts
from app.api.znt.schemas import Post

router = APIRouter()


@router.get("/posts", response_model=List[Post], status_code=200)
async def all_posts():
    query = posts.select()
    all_posts = await database.fetch_all(query)
    if posts is None:
        return {"message": " No post found!"}
    else:
        return all_posts


@router.get("/post/{id}", response_model=Post, status_code=200)
async def get_post(id:int):
    query = posts.select().where(posts.c.id == id)
    return await database.fetch_one(query=query)


@router.post("/create/", response_model=Post, status_code=201)
async def create(post: Post):
    query = posts.insert().values(title=post.title, body=post.body, is_published=post.is_published,
                                  created=post.created, modified=post.modified)
    last_record_id = await database.execute(query=query)
    return {**post.dict(), "id": last_record_id}


@router.patch("/update/{id}", response_model=Post)
async def update(id:int, post: Post):
    query = posts.update().where(posts.c.id == id).values(title=post.title, body=post.body,
                                                          is_published=post.is_published, created=post.created,
                                                          modified=post.modified)
    last_record_id = await database.execute(query=query)
    return {**post.dict(), "id": last_record_id}


@router.delete("/delete/{id}", response_model=Post)
async def delete(id:int):
    query = posts.delete().where(posts.c.id == id)
    return await database.execute(query)
