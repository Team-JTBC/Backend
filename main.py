# main.py

from fastapi import FastAPI, File, UploadFile, Form
import logging
from fastapi.middleware.cors import CORSMiddleware
from db_connection import database, posts
from fastapi.responses import JSONResponse
from pathlib import Path
import os
from datetime import datetime
from pydantic import BaseModel
from typing import List
from fastapi.responses import FileResponse


app = FastAPI()
UPLOAD_DIR = "./images"

logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO)

origins = [
    "*", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Post(BaseModel):
    title: str
    content: str
    category: str

@app.on_event("startup")
async def startup_db_client():
    await database.connect()

@app.on_event("shutdown")
async def shutdown_db_client():
    await database.disconnect()

@app.post("/post")
async def create_post(title: str = Form(...), content: str = Form(...), category: str = Form(...), img: UploadFile = File(...)):
    try:
        image = await img.read()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{img.filename}.jpg"
        print(filename)
        with open(os.path.join(UPLOAD_DIR, filename), "wb") as fp:
            fp.write(image) 
        query = posts.insert().values(title=title, content=content, category = category, imgUrl=f"./images/{filename}")
        await database.execute(query)

        return {"message": "Post created successfully"}
    except Exception as e:
        error_message = str(e)
        return JSONResponse(content={"error": error_message}, status_code=500, media_type="text/plain")
    
@app.get("/post", response_model=List[Post])
async def get_posts():
    query = posts.select()
    queryResults = await database.fetch_all(query)
    print(queryResults)
    
    if not queryResults:
        raise HTTPException(status_code=404, detail="No posts found")
    
    posts_with_images = []

    for result in queryResults:
        post = Post(title=result['title'], content=result['content'], category=result['category'])
        print(post)
        # image_data = await get_image_data(result[3])
        posts_with_images.append({**post.dict()})
    
    return posts_with_images

@app.get("/post/{post_id}", response_model=List[Post])
async def get_posts(post_id:int):
    query = posts.select().where(posts.c.id == post_id)
    queryResults = await database.fetch_all(query)
    print(queryResults)
    
    if not queryResults:
        raise HTTPException(status_code=404, detail="No posts found")
    
    posts_with_images = []

    for result in queryResults:
        post = Post(title=result['title'], content=result['content'], category=result['category'])
        print(post)
        # image_data = await get_image_data(result[3])
        posts_with_images.append({**post.dict()})
    
    return posts_with_images

@app.put("/post/{post_id}")
async def updatePost(post_id: int,title: str = Form(...), content: str = Form(...), category: str = Form(...), img: UploadFile = File(...)):
    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{img.filename}.jpg"
        with open(os.path.join(UPLOAD_DIR, filename), "wb") as fp:
            fp.write(await img.read())
        query = (
            posts.update()
            .where(posts.c.id == post_id)
            .values(title=title, content=content, category=category, imgUrl=f"./images/{filename}")
        )
        await database.execute(query)

        return {"message": "Post created successfully"}
    except:
        error_message = str(e)
        return JSONResponse(content={"error": error_message}, status_code=500, media_type="text/plain")
    

    

@app.delete("/post/{post_id}")
async def delete_post(post_id: int):
    try:

        query = posts.delete().where(posts.c.id == post_id)
        await database.execute(query)

        return {"message": "Post deleted successfully"}
    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=500, detail=error_message)



async def get_image_data(image_path: str):
    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            return image_data
    except FileNotFoundError:
        # 이미지가 없는 경우 404 에러 처리
        raise HTTPException(status_code=404, detail="Image not found")

    
@app.get("/get_image")
async def get_image():
    # 이미지 파일 경로
    image_path = "./images/IMG_2728.jpg.jpg"
    return FileResponse(image_path, media_type="image/jpeg")

    
