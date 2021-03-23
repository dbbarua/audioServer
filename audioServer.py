from typing import List

import databases
import sqlalchemy
import uvicorn
from fastapi import FastAPI, Form, Query
from pydantic import BaseModel

# Test project for Interview
# Create a FastAPI for uploading audio files
# Developer : Deepak Barua <dbbarua@icloud.com>
# Date : 23 Mar 2021

# SQLAlchemy specific code, as with any other app
DATABASE_URL = "sqlite:///./test.db"
# DATABASE_URL = "postgresql://user:password@postgresserver/db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

notes = sqlalchemy.Table(
    "notes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("Type", sqlalchemy.String),
    sqlalchemy.Column("Name", sqlalchemy.String),
    sqlalchemy.Column("Duration", sqlalchemy.BigInteger),
    sqlalchemy.Column("Upload Time", sqlalchemy.DateTime),
    sqlalchemy.Column("Author", sqlalchemy.String),
    sqlalchemy.Column("Host/Narrator", sqlalchemy.String),
    sqlalchemy.Column("Upload Time", sqlalchemy.DateTime),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)


class NoteIn(BaseModel):
    text: str
    completed: bool


class Note(BaseModel):
    id: int
    text: str
    completed: bool


app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/notes/", response_model=List[Note])
async def read_notes():
    query = notes.select()
    return await database.fetch_all(query)


@app.post("/notes/", response_model=Note)
async def create_note(note: NoteIn):
    query = notes.insert().values(text=note.text, completed=note.completed)
    last_record_id = await database.execute(query)
    return {**note.dict(), "id": last_record_id}


@app.post("/login/")
async def login(_q: str = Query("eu", enum=["SONG", "PODCAST", "AUDIOBOOK"])):
    return {"username": _q}


if __name__ == '__main__':
    uvicorn.run(app)
