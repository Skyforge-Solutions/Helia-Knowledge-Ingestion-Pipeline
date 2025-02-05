from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
import uvicorn
import re
from typing import Optional
from urllib.parse import urlparse

from db_setup import SessionLocal, engine, Base
from models import ResourceLink

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def validate_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except:
        return False

def validate_pdf_url(url: str) -> bool:
    return validate_url(url) and url.lower().endswith('.pdf')

@app.get("/upload", response_class=HTMLResponse)
def show_form(request: Request):
    return templates.TemplateResponse("upload_form.html", {"request": request})

@app.post("/upload")
async def handle_form(
    request: Request,
    bot_name: str = Form(...),
    pdf_links: str = Form(""),
    blog_links: str = Form(""),
    db: Session = Depends(get_db)
):
    if not bot_name or bot_name.strip() == "":
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Bot name is required"
            }
        )

    pdf_list = [url.strip() for url in re.split(r"[\n,]+", pdf_links.strip()) if url.strip()]
    blog_list = [url.strip() for url in re.split(r"[\n,]+", blog_links.strip()) if url.strip()]
    
    if not pdf_list and not blog_list:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "At least one URL is required"
            }
        )

    # Check for duplicates between PDF and blog lists
    duplicates = set(pdf_list) & set(blog_list)
    if duplicates:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Same URL cannot be in both PDF and blog sections"
            }
        )

    try:
        new_records_count = 0
        skipped_urls = []

        # First, check all URLs for existing records
        all_urls = pdf_list + blog_list
        existing_links = db.query(ResourceLink).filter(
            ResourceLink.link.in_(all_urls),
            ResourceLink.bot_name == bot_name
        ).all()
        
        existing_urls = {link.link for link in existing_links}
        
        # Process PDF links
        for url in pdf_list:
            if url in existing_urls:
                skipped_urls.append(url)
                continue
                
            link = ResourceLink(
                link=url,
                file_type="pdf",
                bot_name=bot_name,
                processing_status="pending",
                is_embedded=False
            )
            db.add(link)
            new_records_count += 1

        # Process blog links
        for url in blog_list:
            if url in existing_urls:
                skipped_urls.append(url)
                continue
                
            link = ResourceLink(
                link=url,
                file_type="blog",
                bot_name=bot_name,
                processing_status="pending",
                is_embedded=False
            )
            db.add(link)
            new_records_count += 1

        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            if isinstance(e.orig, UniqueViolation):
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": "error",
                        "message": "Duplicate URLs detected. Please refresh and try again."
                    }
                )
            raise e

        # Build response message
        if new_records_count > 0:
            message = "Upload successful"
            if skipped_urls:
                message += f" ({len(skipped_urls)} duplicates skipped)"
        else:
            message = "All URLs were duplicates"

        return JSONResponse(
            status_code=200,
            content={
                "status": "success" if new_records_count > 0 else "warning",
                "message": message,
                "new_count": new_records_count,
                "skipped_urls": skipped_urls
            }
        )
            
    except Exception as e:
        db.rollback()
        print(f"Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Server error. Please try again."
            }
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
