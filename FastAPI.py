from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI()

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["blog_platform"]
posts_collection = db["posts"]

# Define Pydantic models for data validation
class Post(BaseModel):
    title: str
    content: str

class Comment(BaseModel):
    content: str

class Like(BaseModel):
    action: str  # 'like' or 'dislike'

# Define MongoDB data access methods
class MongoDBManager:
    @staticmethod
    def create_post(post: Post):
        return posts_collection.insert_one(post.dict()).inserted_id

    @staticmethod
    def get_post(post_id: str):
        return posts_collection.find_one({"_id": ObjectId(post_id)})

    @staticmethod
    def update_post(post_id: str, post: Post):
        posts_collection.update_one({"_id": ObjectId(post_id)}, {"$set": post.dict()})

    @staticmethod
    def delete_post(post_id: str):
        posts_collection.delete_one({"_id": ObjectId(post_id)})

    @staticmethod
    def create_comment(post_id: str, comment: Comment):
        posts_collection.update_one({"_id": ObjectId(post_id)}, {"$push": {"comments": comment.dict()}})

    @staticmethod
    def like_post(post_id: str, action: str):
        posts_collection.update_one({"_id": ObjectId(post_id)}, {"$inc": {"likes" if action == "like" else "dislikes": 1}})

# Define API endpoints
@app.post("/posts/")
async def create_post(post: Post):
    post_id = MongoDBManager.create_post(post)
    return {"post_id": str(post_id)}

@app.get("/posts/{post_id}/")
async def read_post(post_id: str):
    post = MongoDBManager.get_post(post_id)
    if post:
        return post
    else:
        raise HTTPException(status_code=404, detail="Post not found")

@app.put("/posts/{post_id}/")
async def update_post(post_id: str, post: Post):
    MongoDBManager.update_post(post_id, post)
    return {"message": "Post updated successfully"}

@app.delete("/posts/{post_id}/")
async def delete_post(post_id: str):
    MongoDBManager.delete_post(post_id)
    return {"message": "Post deleted successfully"}

@app.post("/posts/{post_id}/comments/")
async def create_comment(post_id: str, comment: Comment):
    MongoDBManager.create_comment(post_id, comment)
    return {"message": "Comment added successfully"}

@app.post("/posts/{post_id}/like/")
async def like_post(post_id: str, like: Like):
    MongoDBManager.like_post(post_id, like.action)
    return {"message": "Post liked successfully"}

@app.post("/posts/{post_id}/dislike/")
async def dislike_post(post_id: str, like: Like):
    MongoDBManager.like_post(post_id, like.action)
    return {"message": "Post disliked successfully"}
