from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import pytesseract
from PIL import Image
import io
import uuid
from datetime import datetime
import json
import re

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="F-AI AuthX API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Set Tesseract path for Windows (adjust based on your installation)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@app.get("/")
def read_root():
    return {"message": "F-AI AuthX API is running"}

@app.post("/api/users/create")
async def create_user(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    date_of_birth: str = Form(...),
    address: str = Form(...)
):
    """Create a new user and return user_id"""
    try:
        # Insert user into database
        response = supabase.table("users").insert({
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone_number": phone_number,
            "date_of_birth": date_of_birth,
            "address": address
        }).execute()
        
        user_data = response.data[0]
        user_id = user_data['id']
        
        # Create verification record
        supabase.table("verifications").insert({
            "user_id": user_id
        }).execute()
        
        return {"success": True, "user_id": user_id, "message": "User created successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/documents/upload")
async def upload_document(
    user_id: str = Form(...),
    document_type: str = Form(...),
    document_number: str = Form(...),
    document_image: UploadFile = File(...),
    user_dob: str = Form(...)
):
    """Upload document image, perform OCR, and verify"""
    try:
        # Read image
        image_bytes = await document_image.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Perform OCR
        ocr_text = pytesseract.image_to_string(image)
        
        # Extract document number and DOB from OCR text
        extracted_doc_number = extract_document_number(ocr_text, document_type)
        extracted_dob = extract_date_of_birth(ocr_text)
        
        # Verify document number match
        doc_number_match = verify_document_number(document_number, extracted_doc_number)
        
        # Verify DOB match
        dob_match = verify_dob(user_dob, extracted_dob)
        
        # Upload image to Supabase Storage
        file_name = f"{user_id}_{document_type}_{uuid.uuid4()}.jpg"
        supabase.storage.from_("document-images").upload(
            file_name,
            image_bytes,
            {"content-type": "image/jpeg"}
        )
        
        # Get public URL
        document_url = supabase.storage.from_("document-images").get_public_url(file_name)
        
        # Save document info to database
        supabase.table("documents").insert({
            "user_id": user_id,
            "document_type": document_type,
            "document_number": document_number,
            "extracted_document_number": extracted_doc_number,
            "extracted_date_of_birth": extracted_dob,
            "document_image_url": document_url
        }).execute()
        
        # Update verification status
        supabase.table("verifications").update({
            "document_number_match": doc_number_match,
            "dob_match": dob_match,
            "age_verified": dob_match,
            "document_originality_verified": True,  # Can add more sophisticated checks
            "ocr_data": {
                "raw_text": ocr_text,
                "extracted_doc_number": extracted_doc_number,
                "extracted_dob": extracted_dob
            }
        }).eq("user_id", user_id).execute()
        
        return {
            "success": True,
            "document_url": document_url,
            "ocr_text": ocr_text,
            "extracted_doc_number": extracted_doc_number,
            "extracted_dob": extracted_dob,
            "doc_number_match": doc_number_match,
            "dob_match": dob_match
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/images/upload-selfie")
async def upload_selfie(
    user_id: str = Form(...),
    selfie_image: UploadFile = File(...)
):
    """Upload selfie image"""
    try:
        image_bytes = await selfie_image.read()
        
        # Upload to Supabase Storage
        file_name = f"{user_id}_selfie_{uuid.uuid4()}.jpg"
        supabase.storage.from_("selfie-images").upload(
            file_name,
            image_bytes,
            {"content-type": "image/jpeg"}
        )
        
        selfie_url = supabase.storage.from_("selfie-images").get_public_url(file_name)
        
        # Update verification record
        supabase.table("verifications").update({
            "selfie_image_url": selfie_url
        }).eq("user_id", user_id).execute()
        
        return {"success": True, "selfie_url": selfie_url}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/images/upload-live-preview")
async def upload_live_preview(
    user_id: str = Form(...),
    live_image: UploadFile = File(...)
):
    """Upload live camera snapshot"""
    try:
        image_bytes = await live_image.read()
        
        # Upload to Supabase Storage
        file_name = f"{user_id}_live_{uuid.uuid4()}.jpg"
        supabase.storage.from_("live-preview-images").upload(
            file_name,
            image_bytes,
            {"content-type": "image/jpeg"}
        )
        
        live_url = supabase.storage.from_("live-preview-images").get_public_url(file_name)
        
        # Update verification record
        supabase.table("verifications").update({
            "live_preview_image_url": live_url
        }).eq("user_id", user_id).execute()
        
        return {"success": True, "live_url": live_url}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/verify/face-similarity")
async def verify_face_similarity(
    user_id: str = Form(...)
):
    """
    Verify face similarity using Buffalo model
    NOTE: This is a placeholder. You'll integrate the trained Buffalo model here.
    """
    try:
        # TODO: Implement Buffalo face recognition model here
        # For now, return a mock similarity score
        
        # Get verification record
        verification = supabase.table("verifications").select("*").eq("user_id", user_id).execute()
        
        if not verification.data:
            raise HTTPException(status_code=404, detail="Verification record not found")
        
        # Placeholder for Buffalo model integration
        # similarity_score = buffalo_model.compare_faces(selfie_url, live_url)
        
        # Mock similarity score for demonstration
        similarity_score = 85.5  # This will be replaced with actual Buffalo model output
        
        is_verified = similarity_score >= 75.0  # Threshold
        
        # Update verification status
        supabase.table("verifications").update({
            "face_similarity_percentage": similarity_score,
            "face_similarity_verified": is_verified
        }).eq("user_id", user_id).execute()
        
        return {
            "success": True,
            "similarity_score": similarity_score,
            "is_verified": is_verified
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/biometric/upload")
async def upload_biometric(
    user_id: str = Form(...),
    biometric_image: UploadFile = File(...)
):
    """Upload biometric data"""
    try:
        image_bytes = await biometric_image.read()
        
        # Upload to Supabase Storage
        file_name = f"{user_id}_biometric_{uuid.uuid4()}.jpg"
        supabase.storage.from_("biometric-images").upload(
            file_name,
            image_bytes,
            {"content-type": "image/jpeg"}
        )
        
        biometric_url = supabase.storage.from_("biometric-images").get_public_url(file_name)
        
        # Update verification record
        supabase.table("verifications").update({
            "biometric_image_url": biometric_url,
            "biometric_verified": True  # Add actual biometric verification logic
        }).eq("user_id", user_id).execute()
        
        return {"success": True, "biometric_url": biometric_url}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/verification/status/{user_id}")
async def get_verification_status(user_id: str):
    """Get verification status for a user"""
    try:
        # Get verification data
        verification = supabase.table("verifications").select("*").eq("user_id", user_id).execute()
        
        if not verification.data:
            raise HTTPException(status_code=404, detail="Verification not found")
        
        return {"success": True, "verification": verification.data[0]}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Helper functions for OCR processing

def extract_document_number(ocr_text: str, doc_type: str) -> Optional[str]:
    """Extract document number based on document type"""
    ocr_text = ocr_text.upper()
    
    # Aadhar: 12 digit number
    if doc_type == "aadhar":
        match = re.search(r'\b\d{4}\s?\d{4}\s?\d{4}\b', ocr_text)
        return match.group(0).replace(" ", "") if match else None
    
    # PAN: 10 character alphanumeric
    elif doc_type == "pan":
        match = re.search(r'\b[A-Z]{5}\d{4}[A-Z]\b', ocr_text)
        return match.group(0) if match else None
    
    # Driving License: varies by state
    elif doc_type == "driving_license":
        match = re.search(r'\b[A-Z]{2}\d{2}\s?\d{11}\b', ocr_text)
        return match.group(0) if match else None
    
    # Passport: 8 characters
    elif doc_type == "passport":
        match = re.search(r'\b[A-Z]\d{7}\b', ocr_text)
        return match.group(0) if match else None
    
    # Voter ID
    elif doc_type == "voter_id":
        match = re.search(r'\b[A-Z]{3}\d{7}\b', ocr_text)
        return match.group(0) if match else None
    
    return None

def extract_date_of_birth(ocr_text: str) -> Optional[str]:
    """Extract date of birth from OCR text"""
    # Common date patterns: DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY
    date_patterns = [
        r'\b(\d{2})[/-](\d{2})[/-](\d{4})\b',
        r'\b(\d{2})\.(\d{2})\.(\d{4})\b',
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, ocr_text)
        if match:
            day, month, year = match.groups()
            return f"{year}-{month}-{day}"  # Return in ISO format
    
    return None

def verify_document_number(entered_number: str, extracted_number: Optional[str]) -> bool:
    """Verify if document numbers match"""
    if not extracted_number:
        return False
    
    # Remove spaces and compare
    entered_clean = entered_number.replace(" ", "").upper()
    extracted_clean = extracted_number.replace(" ", "").upper()
    
    return entered_clean == extracted_clean

def verify_dob(entered_dob: str, extracted_dob: Optional[str]) -> bool:
    """Verify if dates of birth match"""
    if not extracted_dob:
        return False
    
    return entered_dob == extracted_dob

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
