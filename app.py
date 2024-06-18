
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List
from bson import ObjectId

from models import *
from database import db
from auth import *
from utils import rate_limit

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

@app.post("/api/auth/signup")
async def signup(request:Request, user: User):
    if db.users.find_one({"username": user.username}):
        raise HTTPException(
            status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(user.password)
    user_dict = {"username": user.username, "password": hashed_password}
    db.users.insert_one(user_dict)

    return {"message": "User created successfully"}


@app.post("/api/auth/login")
async def login(request:Request, form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.users.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=400, detail="Invalid username or password")

    access_token = create_access_token(data={"username": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(request:Request, token: str = Depends(oauth2_scheme)):
    username = decode_access_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@app.post("/api/notes")
@rate_limit(limit=2,window_seconds=30)
async def create_note(request:Request, note: Note, current_user: dict = Depends(get_current_user)):
    note_dict = note.model_dump()
    note_dict.update({"user_id": current_user["_id"]})
    db.notes.insert_one(note_dict)
    return {"message": "Note created successfully"}

@app.get("/api/notes", response_model=List[Note])
@rate_limit(limit=2,window_seconds=30)
async def get_notes(request:Request,current_user: dict = Depends(get_current_user)):
    notes = list(db.notes.find({"user_id": current_user["_id"]}))
    return notes


@app.get("/api/notes/{id}", response_model=Note)
@rate_limit(limit=2,window_seconds=30)
async def get_note_by_id(request:Request, id: str, current_user: dict = Depends(get_current_user)):
    note = db.notes.find_one(
        {"_id": ObjectId(id), "user_id": current_user["_id"]})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.put("/api/notes/{id}")
@rate_limit(limit=2,window_seconds=30)
async def update_note(request:Request, id: str, note: Note, current_user: dict = Depends(get_current_user)):
    result = db.notes.update_one(
        {"_id": ObjectId(id), "user_id": current_user["_id"]},
        {"$set": note.model_dump()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note updated successfully"}


@app.delete("/api/notes/{id}")
@rate_limit(limit=2,window_seconds=30)
async def delete_note(request:Request, id: str, current_user: dict = Depends(get_current_user)):
    result = db.notes.delete_one(
        {"_id": ObjectId(id), "user_id": current_user["_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted successfully"}


@app.post("/api/notes/{id}/share")

async def share_note(request:Request, id: str, username: str, current_user: dict = Depends(get_current_user)):
    user_to_share = db.users.find_one({"username": username})
    if not user_to_share:
        raise HTTPException(status_code=404, detail="User not found")

    note = db.notes.find_one(
        {"_id": ObjectId(id), "user_id": current_user["_id"]})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if username in note["shared_with"]:
        raise HTTPException(
            status_code=400, detail="Note already shared with this user")

    db.notes.update_one(
        {"_id": ObjectId(id), "user_id": current_user["_id"]},
        {"$push": {"shared_with": username}}
    )
    return {"message": "Note shared successfully"}


@app.get("/api/search")
async def search_notes(request:Request, q: str, current_user: dict = Depends(get_current_user)):
    notes = list(db.notes.find(
        {"$text": {"$search": q}, "user_id": current_user["_id"]}
    ))

    # Convert MongoDB documents to JSON serializable format
    for note in notes:
        note["_id"] = str(note["_id"])
        note["user_id"] = str(note["user_id"])

    return notes
