import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import create_document, get_documents
from schemas import ContactMessage

app = FastAPI(title="College Website API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Shri Ghanshyam Dubey Degree College Suriyawan API"}

# Public content endpoints

@app.get("/api/college")
def get_college_info():
    return {
        "name": "Shri Ghanshyam Dubey Degree College, Suriyawan",
        "tagline": "Empowering Education, Enriching Lives",
        "about": "Shri Ghanshyam Dubey Degree College, Suriyawan is dedicated to providing quality higher education with a focus on academic excellence, character building, and community development.",
        "address": "Suriyawan, Bhadohi, Uttar Pradesh",
        "established": 2005,
        "affiliation": "State University",
        "contact": {
            "email": "info@sgddcollege.ac.in",
            "phone": "+91-XXXXXXXXXX"
        },
        "programs": [
            {"name": "B.A.", "duration": "3 Years", "intake": 120},
            {"name": "B.Sc.", "duration": "3 Years", "intake": 120},
            {"name": "B.Com.", "duration": "3 Years", "intake": 120}
        ],
        "highlights": [
            "Experienced faculty",
            "Modern classrooms",
            "Scholarship support",
            "Active NSS and sports"
        ]
    }

# Contact form endpoint

@app.post("/api/contact")
def submit_contact(message: ContactMessage):
    try:
        doc_id = create_document("contactmessage", message)
        return {"status": "success", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contact")
def list_contacts(limit: int = 20):
    try:
        docs = get_documents("contactmessage", limit=limit)
        # Convert ObjectId and datetime to string for JSON serialization
        def serialize(doc):
            doc = dict(doc)
            if "_id" in doc:
                doc["id"] = str(doc.pop("_id"))
            for k, v in list(doc.items()):
                if hasattr(v, "isoformat"):
                    doc[k] = v.isoformat()
            return doc
        return [serialize(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
