
from fastapi import FastAPI, File, Form, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
from PIL import Image
import imagehash, hashlib, os

# Setup DB
Base = declarative_base()
DB_URL = "sqlite:///./fingerprints.db"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Fingerprint(Base):
    __tablename__ = "fingerprints"
    id = Column(Integer, primary_key=True, index=True)
    hash_value = Column(String, unique=True, index=True)

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def generate_fingerprint(image_bytes: bytes, name: str) -> str:
    with open("temp_image", "wb") as f:
        f.write(image_bytes)
    img = Image.open("temp_image")
    os.remove("temp_image")

    img_hash = str(imagehash.phash(img))
    combined = img_hash + name
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()

@app.post("/upload")
async def upload_file(image: UploadFile = File(...), name: str = Form(...)):
    content = await image.read()
    fingerprint = generate_fingerprint(content, name)

    db = SessionLocal()
    exists = db.query(Fingerprint).filter(Fingerprint.hash_value == fingerprint).first()

    if exists:
        return {"fingerprint": fingerprint, "status": "Blocked"}
    else:
        db.add(Fingerprint(hash_value=fingerprint))
        db.commit()
        return {"fingerprint": fingerprint, "status": "Stored"}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
