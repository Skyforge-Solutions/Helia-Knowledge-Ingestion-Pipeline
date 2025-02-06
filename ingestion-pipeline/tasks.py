# tasks.py
import traceback
from celery_app import celery_app
from sqlalchemy.orm import Session
from db_setup import SessionLocal
from models import ResourceLink

# Suppose you'd store embeddings in Chroma:
# from chromadb_client import get_chroma_collection

@celery_app.task
def process_resource(link: str, bot_name: str, file_type: str):
    """
    1) Set link to 'processing'
    2) Scrape/parse content
    3) Embed
    4) Push to Chroma for the correct bot
    5) Update DB with success/failure
    """
    db: Session = SessionLocal()
    try:
        link_record = db.query(ResourceLink).filter_by(
            link=link,
            bot_name=bot_name
        ).first()

        if not link_record:
            print(f"No ResourceLink found for link={link} bot={bot_name}")
            return

        # Mark as processing
        link_record.processing_status = "processing"
        db.commit()

        # === 1) Scrape content (stub) ===
        # You might do something like:
        # if file_type == "pdf":
        #     text_content = scrape_pdf(link)
        # else:
        #     text_content = scrape_blog(link)
        # We'll pretend we got some text:
        text_content = f"Fake content from {file_type} link: {link}"

        # === 2) Embed content (stub) ===
        # e.g., embed_text(text_content)
        # We'll pretend we have a dummy vector:
        embedding = [0.123, 0.456, 0.789]

        # === 3) Push to Chroma (stub) ===
        # collection = get_chroma_collection(bot_name)
        # collection.add(
        #     documents=[text_content],
        #     embeddings=[embedding],
        #     metadatas=[{"url": link}],
        #     ids=[f"{bot_name}_{link}"]
        # )

        # If all goes well
        link_record.processing_status = "completed"
        link_record.is_embedded = True
        link_record.error_message = None
        db.commit()

    except Exception as e:
        db.rollback()
        print("Error processing link:", traceback.format_exc())
        link_record = db.query(ResourceLink).filter_by(
            link=link,
            bot_name=bot_name
        ).first()
        if link_record:
            link_record.processing_status = "failed"
            link_record.error_message = str(e)
            db.commit()

    finally:
        db.close()
