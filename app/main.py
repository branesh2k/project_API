from fastapi import FastAPI, HTTPException, status, Response, Depends
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from typing import List
from . import models, schemas
from .database import engine, get_db
from sqlalchemy.orm import Session


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


while True:
    try:
        conn = psycopg2.connect(database="postgres", user="postgres",
                                password="12345", cursor_factory=RealDictCursor)
        cur = conn.cursor()
        print("connection successful")
        break
    except Exception as error:
        print(f"connection failed :{error}")
        time.sleep(3)


@app.get('/')
def homepage():
    return {"DATA": " Home Page "}


@app.get('/posts', response_model=List[schemas.Post])
def all_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Posts).all()
    return posts


@app.get('/post/{id}', response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Posts).filter(models.Posts.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id={id} not found")
    return post


@app.post('/new_post', status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def new_post(post: schemas.PostBase, db: Session = Depends(get_db)):
    newpost = models.Posts(**post.dict())
    db.add(newpost)
    db.commit()
    db.refresh(newpost)
    return newpost


@app.delete('/post/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    deleted_post = db.query(models.Posts).filter(models.Posts.id == id)

    if deleted_post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id={id} not found")
    deleted_post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put('/post/{id}', response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    updated_post_query = db.query(models.Posts).filter(models.Posts.id == id)
    updated_post = updated_post_query.first()
    updated_post_query.update(post.dict(), synchronize_session=False)

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id={id} not found")
    db.commit()
    return updated_post
