# main.py
from fastapi import FastAPI, Request, Form, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import uvicorn
import re  # for simple link checks

from db_setup import SessionLocal, engine, Base
from models import ResourceLink

# Create tables on startup (for quick demo). In production, use migrations.
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/upload", response_class=HTMLResponse)
def show_form(request: Request):
    return templates.TemplateResponse("upload_form.html", {"request": request})

@app.post("/upload")
async def handle_form(
    request: Request,
    bot_name: str = Form(...),
    pdf_links: str = Form(""),
    blog_links: str = Form(""),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    print("\n=== Received Form Submission ===")
    print(f"Bot Name: {bot_name}")
    
    # Parse and print PDF links
    pdf_list = [url.strip() for url in re.split(r"[\n,]+", pdf_links.strip()) if url.strip()]
    print("\nPDF Links:")
    for i, url in enumerate(pdf_list, 1):
        print(f"{i}. {url}")
    
    # Parse and print blog links
    blog_list = [url.strip() for url in re.split(r"[\n,]+", blog_links.strip()) if url.strip()]
    print("\nBlog Links:")
    for i, url in enumerate(blog_list, 1):
        print(f"{i}. {url}")
    
    print("\n" + "="*30 + "\n")

    try:
        new_records_count = 0
        skipped_urls = []

        # Process PDF links
        for url in pdf_list:
            if url.startswith("http") and ".pdf" in url.lower():
                # Check if URL already exists for this bot
                existing_link = db.query(ResourceLink).filter(
                    ResourceLink.link == url,
                    ResourceLink.bot_name == bot_name
                ).first()
                
                if existing_link:
                    print(f"Skipping duplicate URL for bot {bot_name}: {url}")
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
            if url.startswith("http"):
                # Check if URL already exists for this bot
                existing_link = db.query(ResourceLink).filter(
                    ResourceLink.link == url,
                    ResourceLink.bot_name == bot_name
                ).first()
                
                if existing_link:
                    print(f"Skipping duplicate URL for bot {bot_name}: {url}")
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

        db.commit()

        if background_tasks and new_records_count > 0:
            background_tasks.add_task(process_new_links, bot_name)

        message = f"Successfully added {new_records_count} new links for bot {bot_name}!"
        if skipped_urls:
            message += f"\n\nSkipped {len(skipped_urls)} duplicate URLs:"
            for url in skipped_urls:
                message += f"\n• {url}"
            
        return {
            "status": "success",
            "message": message,
            "new_count": new_records_count,
            "skipped_urls": skipped_urls
        }
    except Exception as e:
        db.rollback()
        print(f"Error: {str(e)}")
        return {"status": "error", "message": "An error occurred while processing your request."}

def process_new_links(bot_name: str):
    """
    Background task to process newly added links for a specific bot.
    E.g., scraping, PDF parsing, embedding in Chroma, etc.
    """
    db = SessionLocal()
    try:
        # Fetch all 'pending' links for this bot
        pending_links = db.query(ResourceLink).filter(
            ResourceLink.bot_name == bot_name,
            ResourceLink.processing_status == "pending"
        ).all()

        for link_rec in pending_links:
            print(f"\nProcessing link: {link_rec.link}")
            link_rec.processing_status = "processing"
            db.commit()

            # Try the actual crawling / PDF extraction / embedding
            try:
                # For now, we'll leave the link in 'processing' state
                # The actual embedding process will update these statuses
                # when it processes the links
                print(f"Link {link_rec.link} marked for processing")
                
                # Note: Remove this comment when implementing the actual processing:
                # - PDF parser for link_rec.file_type == 'pdf'
                # - crawl4ai or requests/BeautifulSoup for blog
                # - embed with chosen embedding model
                # - store results in Chroma DB instance for this bot
                
            except Exception as e:
                print(f"Error processing {link_rec.link}: {str(e)}")
                link_rec.is_embedded = False
                link_rec.processing_status = "failed"
                link_rec.error_message = str(e)
                db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    # Start the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
