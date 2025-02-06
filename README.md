# 🚀 Helia-Knowledge-Ingestion-Pipeline
A **scalable AI knowledge ingestion pipeline** that extracts, embeds, and integrates external data into **Google Gemini** for AI-enhanced chatbot responses.

---

## 🏗 **Pipeline Architecture**
### **1️⃣ Data Ingestion**
- Users submit **PDFs or Blog URLs** via a FastAPI form.
- Links are **stored in PostgreSQL** (`resource_links` table).
- **Celery + RabbitMQ** queues background tasks for processing.

### **2️⃣ Processing & Embedding**
- **Celery worker processes each link asynchronously**:
  - **PDFs** → Extracted using `pymupdf` (`fitz`).
  - **Blogs** → Scraped using `trafilatura`.
  - Text is **embedded using OpenAI's `text-embedding-ada-002`**.
  - Embeddings & raw text are **stored in ChromaDB** for retrieval.

### **3️⃣ Retrieval & AI Response**
- **Chatbot query received via Next.js frontend**.
- **Relevant text chunks** retrieved from **ChromaDB** (based on user question).
- Retrieved knowledge **appended to Gemini API request as context**.
- **Gemini generates AI response using custom knowledge**.
- **Response returned to Next.js frontend** for display.

---

## 🌐 **Deployment Details (GCP & External Services)**
| Component | Deployment |
|-----------|------------|
| **FastAPI Backend** | Hosted on **GCP Compute Engine** |
| **PostgreSQL DB** | Managed on **Google Cloud SQL** |
| **RabbitMQ Broker** | Running on **GCP VM** → [RabbitMQ Dashboard](http://34.47.190.56:15672/#/) |
| **ChromaDB** | Running on **GCP VM** (Containerized) |
| **ChromaDB Dashboard** | [Vector DB Collections](http://35.232.242.250:8501/) |
| **Celery Worker** | Hosted on the **same GCP instance as FastAPI** |
---

## 🛠 **Tech Stack & How Each is Used**
| Technology | Purpose |
|------------|---------|
| **FastAPI** | Backend API handling user inputs & chat queries |
| **Celery + RabbitMQ** | Asynchronous background task processing |
| **PostgreSQL** | Database for tracking link processing status |
| **ChromaDB** | Vector search database storing extracted knowledge |
| **Google Gemini API** | AI-powered chatbot responses |
| **PyMuPDF (fitz)** | PDF text extraction |
| **Trafilatura** | Blog/web content extraction |
| **OpenAI Embeddings** | Converts text into vector embeddings for search |
| **Docker (ChromaDB & RabbitMQ)** | Containerized services running on GCP |

---


