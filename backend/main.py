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
from dateutil import parser as date_parser
import cv2
import numpy as np

# NEW: Face verification imports
import insightface
from insightface.app import FaceAnalysis
from deepface import DeepFace
import requests
import tempfile

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="F-AI AuthX API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Initialize InsightFace Buffalo model
print("Loading InsightFace Buffalo model...")
face_app = FaceAnalysis(
    name='buffalo_l',
    providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
)
face_app.prepare(ctx_id=0, det_size=(640, 640))
print("✅ Face recognition model loaded!")


# ===== FACE VERIFICATION FUNCTIONS =====

def extract_face_from_image(image_bytes: bytes) -> Optional[dict]:
    """
    Extract face from image and return face data with embedding
    
    Args:
        image_bytes: Image as bytes
    
    Returns:
        dict with embedding, bbox, confidence or None
    """
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return None
        
        # Detect faces
        faces = face_app.get(img)
        
        if len(faces) == 0:
            return None
        
        # Get largest face (most prominent)
        face = max(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
        
        return {
            'embedding': face.embedding.tolist(),  # Convert to list for JSON storage
            'bbox': face.bbox.tolist(),
            'confidence': float(face.det_score)
        }
    
    except Exception as e:
        print(f"Error extracting face: {e}")
        return None


def compare_face_embeddings(embedding1: list, embedding2: list, threshold: float = 0.20) -> dict:
    """
    Compare two face embeddings using cosine similarity
    
    Args:
        embedding1: First face embedding (512-dim)
        embedding2: Second face embedding (512-dim)
        threshold: Similarity threshold (default 0.40)
    
    Returns:
        dict with match status and similarity score
    """
    try:
        emb1 = np.array(embedding1)
        emb2 = np.array(embedding2)
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        
        # Convert to percentage
        similarity_percentage = ((similarity + 1) / 2) * 100
        
        # Convert numpy types to Python native types for JSON serialization
        return {
            'match': bool(similarity >= threshold),  # Convert numpy.bool_ to bool
            'similarity': float(similarity),
            'similarity_percentage': float(similarity_percentage),
            'threshold': float(threshold)
        }
    
    except Exception as e:
        print(f"Error comparing embeddings: {e}")
        return {
            'match': False,
            'similarity': 0.0,
            'similarity_percentage': 0.0,
            'error': str(e)
        }


def check_liveness(image_bytes: bytes) -> dict:
    """
    Check if image is from a real person (liveness detection)
    
    Args:
        image_bytes: Image as bytes
    
    Returns:
        dict with liveness status
    """
    try:
        # Save to temp file for DeepFace
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name
        
        # Perform anti-spoofing analysis
        result = DeepFace.extract_faces(
            img_path=tmp_path,
            anti_spoofing=True,
            detector_backend='opencv'
        )
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        if len(result) == 0:
            return {
                'success': False,
                'is_real': False,
                'confidence': 0.0,
                'error': 'No face detected'
            }
        
        face_result = result[0]
        is_real = face_result.get('is_real', False)
        antispoof_score = face_result.get('antispoof_score', 0.0)
        
        # Convert all values to Python native types
        return {
            'success': True,
            'is_real': bool(is_real),  # Ensure it's Python bool
            'confidence': float(antispoof_score),
            'passed': bool(is_real and antispoof_score >= 0.5)  # Ensure it's Python bool
        }
    
    except Exception as e:
        print(f"Error in liveness detection: {e}")
        return {
            'success': False,
            'is_real': False,
            'confidence': 0.0,
            'error': str(e)
        }



def download_image_from_supabase(url: str) -> Optional[bytes]:
    """
    Download image from Supabase storage URL
    
    Args:
        url: Public URL of image in Supabase storage
    
    Returns:
        Image as bytes or None
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        return None
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None


# def check_liveness(image_bytes: bytes) -> dict:
#     """
#     Check if image is from a real person (liveness detection)
    
#     Args:
#         image_bytes: Image as bytes
    
#     Returns:
#         dict with liveness status
#     """
#     try:
#         # Save to temp file for DeepFace
#         with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
#             tmp.write(image_bytes)
#             tmp_path = tmp.name
        
#         # Perform anti-spoofing analysis
#         result = DeepFace.extract_faces(
#             img_path=tmp_path,
#             anti_spoofing=True,
#             detector_backend='opencv'
#         )
        
#         # Clean up temp file
#         os.unlink(tmp_path)
        
#         if len(result) == 0:
#             return {
#                 'success': False,
#                 'is_real': False,
#                 'confidence': 0.0,
#                 'error': 'No face detected'
#             }
        
#         face_result = result[0]
#         is_real = face_result.get('is_real', False)
#         antispoof_score = face_result.get('antispoof_score', 0.0)
        
#         return {
#             'success': True,
#             'is_real': is_real,
#             'confidence': float(antispoof_score),
#             'passed': is_real and antispoof_score >= 0.5
#         }
    
#     except Exception as e:
#         print(f"Error in liveness detection: {e}")
#         return {
#             'success': False,
#             'is_real': False,
#             'confidence': 0.0,
#             'error': str(e)
#         }


# ===== DATE HANDLING FUNCTIONS =====
# (Keep all your existing date functions here)

def normalize_date_string(date_str: str) -> str:
    if not date_str:
        return ""
    date_str = ' '.join(date_str.split())
    replacements = {
        'st': '', 'nd': '', 'rd': '', 'th': '',
        'of': '', 'the': '',
        '/': '-', '.': '-',
    }
    for old, new in replacements.items():
        date_str = date_str.replace(old, new)
    return date_str.strip()


def extract_date_of_birth(ocr_text: str) -> list:
    dates_found = []
    if not ocr_text:
        return dates_found
    ocr_text = normalize_date_string(ocr_text)
    date_patterns = [
        r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b',
        r'\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b',
        r'\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b',
    ]
    for pattern in date_patterns:
        matches = re.findall(pattern, ocr_text, re.IGNORECASE)
        for match in matches:
            try:
                date_string = '-'.join(str(m) for m in match)
                parsed_date = date_parser.parse(date_string, fuzzy=True)
                if 1900 <= parsed_date.year <= datetime.now().year:
                    dates_found.append(parsed_date)
            except:
                continue
    return dates_found


def parse_date_flexible(date_input: str) -> Optional[datetime]:
    if not date_input:
        return None
    try:
        date_input = normalize_date_string(str(date_input))
        parsed_date = date_parser.parse(date_input, fuzzy=True, dayfirst=True)
        return parsed_date
    except:
        return None


def compare_dates_flexible(date1_str: str, date2_str: str) -> dict:
    result = {
        'match': False,
        'similarity_score': 0.0,
        'match_type': 'no_match'
    }
    date1 = parse_date_flexible(date1_str)
    date2 = parse_date_flexible(date2_str)
    if not date1 or not date2:
        return result
    if date1.date() == date2.date():
        result['match'] = True
        result['similarity_score'] = 1.0
        result['match_type'] = 'exact'
        return result
    if date1.year == date2.year:
        if date1.day == date2.month and date1.month == date2.day:
            result['match'] = True
            result['similarity_score'] = 0.95
            result['match_type'] = 'day_month_swapped'
    return result
# ===== ADD THESE TWO NEW FUNCTIONS =====

def improve_image_for_ocr(image: Image.Image) -> Image.Image:
    """Preprocess image for better OCR results"""
    img_array = np.array(image)
    img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
    return Image.fromarray(denoised)


def extract_text_with_multiple_methods(image: Image.Image) -> str:
    """Try multiple OCR methods to extract text"""
    texts = []
    
    # Method 1: Original
    try:
        texts.append(pytesseract.image_to_string(image))
    except:
        pass
    
    # Method 2: Preprocessed
    try:
        improved_img = improve_image_for_ocr(image)
        texts.append(pytesseract.image_to_string(improved_img))
    except:
        pass
    
    # Method 3: Custom config
    try:
        custom_config = r'--oem 3 --psm 6'
        texts.append(pytesseract.image_to_string(image, config=custom_config))
    except:
        pass
    
    return "\n".join(texts)
# ===== DE-DUPLICATION FUNCTION =====

# def check_duplicate_user(new_embedding: list, comparison_type: str) -> dict:
#     """
#     Check if face embedding matches any existing user in database
    
#     Args:
#         new_embedding: Face embedding from new user (512-dim)
#         comparison_type: 'document', 'selfie', or 'live'
    
#     Returns:
#         dict with duplicate status and matching users
#     """
#     try:
#         # Get all existing embeddings of this type
#         if comparison_type == 'document':
#             field = 'document_face_embedding'
#         elif comparison_type == 'selfie':
#             field = 'selfie_face_embedding'
#         elif comparison_type == 'live':
#             field = 'live_face_embedding'  # We'll add this field
#         else:
#             return {'error': 'Invalid comparison type'}
        
#         # Fetch all users with this embedding type
#         all_users = supabase.table("verifications").select(
#             f"user_id, {field}"
#         ).not_.is_(field, 'null').execute()
        
#         duplicates = []
#         threshold = 0.40  # Buffalo-L matching threshold
        
#         print(f"Checking {len(all_users.data)} existing {comparison_type} embeddings...")
        
#         # Compare with each existing user (1-to-many matching)
#         for user in all_users.data:
#             stored_embedding = user.get(field)
            
#             if not stored_embedding:
#                 continue
            
#             # Compare faces using Buffalo embeddings
#             comparison = compare_face_embeddings(stored_embedding, new_embedding, threshold)
            
#             if comparison['match']:
#                 duplicates.append({
#                     'user_id': user['user_id'],
#                     'similarity_percentage': comparison['similarity_percentage'],
#                     'similarity_score': comparison['similarity'],
#                     'comparison_type': comparison_type
#                 })
#                 print(f"⚠️  Duplicate found! User: {user['user_id']}, Similarity: {comparison['similarity_percentage']:.2f}%")
        
#         return {
#             'is_duplicate': len(duplicates) > 0,
#             'duplicate_count': len(duplicates),
#             'matches': duplicates,
#             'total_compared': len(all_users.data)
#         }
    
#     except Exception as e:
#         print(f"Error in duplicate check: {e}")
#         return {
#             'is_duplicate': False,
#             'duplicate_count': 0,
#             'matches': [],
#             'error': str(e)
#         }
def check_duplicate_user(new_embedding: list, comparison_type: str, current_user_id: str = None) -> dict:
    """
    Check if face embedding matches any VERIFIED user in database
    (Ignores expired/incomplete registrations)
    
    Args:
        new_embedding: Face embedding from new user (512-dim)
        comparison_type: 'document', 'selfie', or 'live'
        current_user_id: Current user's ID to exclude from comparison
    
    Returns:
        dict with duplicate status and matching users
    """
    try:
        # Get field name
        if comparison_type == 'document':
            field = 'document_face_embedding'
        elif comparison_type == 'selfie':
            field = 'selfie_face_embedding'
        elif comparison_type == 'live':
            field = 'live_face_embedding'
        else:
            return {'error': 'Invalid comparison type'}
        
        # NEW: Only fetch verified users OR non-expired incomplete users
        current_time = datetime.now().isoformat()
        
        # Fetch users where:
        # 1. User is fully verified (no expiry check), OR
        # 2. User is not expired (expiry_date > now)
        all_users = supabase.table("verifications").select(
            f"user_id, {field}, is_fully_verified, expiry_date, registration_status"
        ).not_.is_(field, 'null').execute()
        
        # Filter out expired users and current user
        active_users = []
        for user in all_users.data:
            # Skip current user
            if current_user_id and user['user_id'] == current_user_id:
                continue
            
            # Include if verified
            if user.get('is_fully_verified'):
                active_users.append(user)
                continue
            
            # Include if not expired
            expiry_date = user.get('expiry_date')
            if expiry_date:
                expiry_datetime = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
                if datetime.now(expiry_datetime.tzinfo) <= expiry_datetime:
                    active_users.append(user)
        
        duplicates = []
        threshold = 0.40
        
        print(f"Checking {len(active_users)} active/verified {comparison_type} embeddings...")
        print(f"(Filtered out {len(all_users.data) - len(active_users)} expired/incomplete users)")
        
        # Compare with each active user
        for user in active_users:
            stored_embedding = user.get(field)
            
            if not stored_embedding:
                continue
            
            comparison = compare_face_embeddings(stored_embedding, new_embedding, threshold)
            
            if comparison['match']:
                duplicates.append({
                    'user_id': user['user_id'],
                    'similarity_percentage': comparison['similarity_percentage'],
                    'similarity_score': comparison['similarity'],
                    'comparison_type': comparison_type,
                    'is_verified': user.get('is_fully_verified', False),
                    'status': user.get('registration_status', 'unknown')
                })
                print(f"⚠️  Duplicate found! User: {user['user_id']}, Similarity: {comparison['similarity_percentage']:.2f}%")
        
        return {
            'is_duplicate': len(duplicates) > 0,
            'duplicate_count': len(duplicates),
            'matches': duplicates,
            'total_compared': len(active_users),
            'total_filtered': len(all_users.data) - len(active_users)
        }
    
    except Exception as e:
        print(f"Error in duplicate check: {e}")
        import traceback
        traceback.print_exc()
        return {
            'is_duplicate': False,
            'duplicate_count': 0,
            'matches': [],
            'error': str(e)
        }


def verify_dob_with_retry(user_dob: str, extracted_dates: list) -> dict:
    if not extracted_dates or len(extracted_dates) == 0:
        return {
            'match': False,
            'confidence': 0.0,
            'suggestion': None,
            'extracted_dob': None,
            'message': 'No date of birth found in document'
        }
    best_match = None
    best_score = 0.0
    for extracted_date in extracted_dates:
        comparison = compare_dates_flexible(user_dob, extracted_date.strftime('%Y-%m-%d'))
        if comparison['similarity_score'] > best_score:
            best_score = comparison['similarity_score']
            best_match = comparison
    if best_score >= 0.90:
        return {
            'match': True,
            'confidence': best_score,
            'extracted_dob': extracted_date.strftime('%Y-%m-%d'),
            'message': 'Date of birth verified'
        }
    return {
        'match': False,
        'confidence': best_score,
        'message': 'Date of birth does not match'
    }


def extract_document_number(ocr_text: str, doc_type: str) -> Optional[str]:
    if not ocr_text:
        return None
    ocr_text = ocr_text.upper()
    if doc_type == "aadhar":
        match = re.search(r'\b\d{4}\s?\d{4}\s?\d{4}\b', ocr_text)
        return match.group(0).replace(" ", "") if match else None
    elif doc_type == "pan":
        match = re.search(r'\b[A-Z]{5}\d{4}[A-Z]\b', ocr_text)
        return match.group(0) if match else None
    return None
from datetime import datetime, timedelta
def check_user_expiry(user_id: str) -> dict:
    """
    Check if user registration has expired (1 week from last activity)
    """
    try:
        user = supabase.table("verifications").select("*").eq("user_id", user_id).execute()
        
        if not user.data:
            return {'expired': False, 'exists': False}
        
        user_data = user.data[0]
        is_verified = user_data.get('is_fully_verified', False)
        expiry_date = user_data.get('expiry_date')
        
        # Verified users never expire
        if is_verified:
            return {'expired': False, 'verified': True, 'exists': True}
        
        # Check if expired
        if expiry_date:
            expiry_datetime = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
            is_expired = datetime.now(expiry_datetime.tzinfo) > expiry_datetime
            
            return {
                'expired': is_expired,
                'expiry_date': expiry_date,
                'verified': False,
                'exists': True
            }
        
        return {'expired': False, 'verified': False, 'exists': True}
    
    except Exception as e:
        print(f"Error checking expiry: {e}")
        return {'expired': False, 'exists': False, 'error': str(e)}


def update_last_activity(user_id: str):
    """
    Update last activity timestamp and extend expiry
    """
    try:
        new_expiry = datetime.now() + timedelta(days=7)
        
        supabase.table("verifications").update({
            "last_activity_date": datetime.now().isoformat(),
            "expiry_date": new_expiry.isoformat()
        }).eq("user_id", user_id).execute()
        
    except Exception as e:
        print(f"Error updating activity: {e}")


def mark_as_verified(user_id: str):
    """
    Mark user as fully verified (no expiry)
    """
    try:
        supabase.table("verifications").update({
            "is_fully_verified": True,
            "registration_status": "complete",
            "overall_status": "verified",
            "expiry_date": None  # Verified users don't expire
        }).eq("user_id", user_id).execute()
        
        print(f"✅ User {user_id} marked as fully verified")
    
    except Exception as e:
        print(f"Error marking as verified: {e}")

def verify_document_number(entered_number: str, extracted_number: Optional[str]) -> bool:
    if not extracted_number:
        return False
    entered_clean = entered_number.replace(" ", "").upper()
    extracted_clean = extracted_number.replace(" ", "").upper()
    return entered_clean == extracted_clean


# ===== API ENDPOINTS =====

# @app.get("/")
# def read_root():
#     return {"message": "F-AI AuthX API with Face Verification is running"}
#removing this for ngrok

# @app.post("/api/users/create")
# async def create_user(
#     first_name: str = Form(...),
#     last_name: str = Form(...),
#     email: str = Form(...),
#     phone_number: str = Form(...),
#     date_of_birth: str = Form(...),
#     address: str = Form(...)
# ):
#     """Create a new user and return user_id"""
#     try:
#         response = supabase.table("users").insert({
#             "first_name": first_name,
#             "last_name": last_name,
#             "email": email,
#             "phone_number": phone_number,
#             "date_of_birth": date_of_birth,
#             "address": address
#         }).execute()
        
#         user_data = response.data[0]
#         user_id = user_data['id']
        
#         # Create verification record
#         supabase.table("verifications").insert({
#             "user_id": user_id
#         }).execute()
        
#         return {"success": True, "user_id": user_id, "message": "User created successfully"}
    
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
@app.post("/api/users/create")
async def create_user(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    date_of_birth: str = Form(...),
    address: str = Form(...)
):
    try:
        # Insert user
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
        
        # Create verification record with expiry (7 days from now)
        expiry_date = datetime.now() + timedelta(days=7)
        
        supabase.table("verifications").insert({
            "user_id": user_id,
            "registration_status": "incomplete",
            "is_fully_verified": False,
            "expiry_date": expiry_date.isoformat(),
            "last_activity_date": datetime.now().isoformat()
        }).execute()
        
        print(f"✅ User created with 7-day expiry: {expiry_date}")
        
        return {
            "success": True,
            "user_id": user_id,
            "expiry_date": expiry_date.isoformat(),
            "message": "Registration started. Complete within 7 days."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# @app.post("/api/documents/upload")
# async def upload_document(
#     user_id: str = Form(...),
#     document_type: str = Form(...),
#     document_number: str = Form(...),
#     document_image: UploadFile = File(...),
#     user_dob: str = Form(...)
# ):
#     """Upload document, perform OCR, extract face, and verify"""
#     try:
#         # Read image
#         image_bytes = await document_image.read()
#         image = Image.open(io.BytesIO(image_bytes))
        
#         # Perform OCR
#         # ocr_text = pytesseract.image_to_string(image)
#         ocr_text =extract_text_with_multiple_methods(image)
#         # Extract document number
#         extracted_doc_number = extract_document_number(ocr_text, document_type)
        
#         # Extract dates
#         extracted_dates = extract_date_of_birth(ocr_text)
        
#         # Verify document number
#         doc_number_match = verify_document_number(document_number, extracted_doc_number)
        
#         # Verify DOB
#         dob_verification = verify_dob_with_retry(user_dob, extracted_dates)
        
#         # NEW: Extract face from document
#         face_data = extract_face_from_image(image_bytes)
#         face_detected = face_data is not None
        
#         # Upload to Supabase Storage with folder structure: user_id/document_type_uuid.jpg
#         file_path = f"{user_id}/{document_type}_{uuid.uuid4()}.jpg"
        
#         supabase.storage.from_("document-images").upload(
#             file_path,
#             image_bytes,
#             {"content-type": "image/jpeg"}
#         )
        
#         document_url = supabase.storage.from_("document-images").get_public_url(file_path)
        
#         # Save document info
#         supabase.table("documents").insert({
#             "user_id": user_id,
#             "document_type": document_type,
#             "document_number": document_number,
#             "extracted_document_number": extracted_doc_number,
#             "extracted_date_of_birth": dob_verification.get('extracted_dob'),
#             "document_image_url": document_url
#         }).execute()
        
#         # Update verification with face embedding
#         update_data = {
#             "document_number_match": doc_number_match,
#             "dob_match": dob_verification['match'],
#             "age_verified": dob_verification['match'],
#             "document_originality_verified": True,
#             "document_face_detected": face_detected,
#             "ocr_data": {
#                 "raw_text": ocr_text,
#                 "extracted_doc_number": extracted_doc_number,
#                 "extracted_dates": [d.strftime('%Y-%m-%d') for d in extracted_dates] if extracted_dates else [],
#                 "dob_verification": dob_verification
#             }
#         }
        
#         # Store face embedding if detected
#         if face_detected:
#             update_data["document_face_embedding"] = face_data['embedding']
#             update_data["document_face_confidence"] = face_data['confidence']
        
#         supabase.table("verifications").update(update_data).eq("user_id", user_id).execute()
        
#         return {
#             "success": True,
#             "document_url": document_url,
#             "doc_number_match": doc_number_match,
#             "dob_match": dob_verification['match'],
#             "dob_verification": dob_verification,
#             "face_detected": face_detected,
#             "face_confidence": face_data['confidence'] if face_detected else 0.0,
#             "requires_correction": not dob_verification['match']
#         }
    
#     except Exception as e:
#         print(f"Error in upload_document: {e}")
#         raise HTTPException(status_code=400, detail=str(e))
# @app.post("/api/documents/upload")
# async def upload_document(
#     user_id: str = Form(...),
#     document_type: str = Form(...),
#     document_number: str = Form(...),
#     document_image: UploadFile = File(...),
#     user_dob: str = Form(...)
# ):
#     try:
#         print(f"\n{'='*60}")
#         print(f"Processing {document_type} for user: {user_id}")
#         print(f"{'='*60}")
        
#         image_bytes = await document_image.read()
#         image = Image.open(io.BytesIO(image_bytes))
        
#         # OCR extraction
#         print("Running OCR...")
#         ocr_text = extract_text_with_multiple_methods(image)
#         extracted_doc_number = extract_document_number(ocr_text, document_type)
#         extracted_dates = extract_date_of_birth(ocr_text)
        
#         doc_number_match = verify_document_number(document_number, extracted_doc_number)
#         dob_verification = verify_dob_with_retry(user_dob, extracted_dates)
        
#         # Extract face from document
#         print("\nExtracting face from document...")
#         face_data = extract_face_from_image(image_bytes)
#         face_detected = face_data is not None
        
#         # NEW: Check for duplicates in document faces
#         document_duplicate_check = {'is_duplicate': False, 'matches': []}
        
#         if face_detected:
#             print("\n🔍 Checking for duplicate document faces...")
#             document_duplicate_check = check_duplicate_user(
#                 face_data['embedding'], 
#                 'document'
#             )
            
#             if document_duplicate_check['is_duplicate']:
#                 print(f"⚠️  ALERT: Found {document_duplicate_check['duplicate_count']} duplicate(s)!")
#                 # Still proceed but flag as duplicate
        
#         # Upload to Supabase Storage
#         file_path = f"{user_id}/{document_type}_{uuid.uuid4()}.jpg"
#         supabase.storage.from_("document-images").upload(
#             file_path, image_bytes, {"content-type": "image/jpeg"}
#         )
#         document_url = supabase.storage.from_("document-images").get_public_url(file_path)
        
#         # Save to database
#         supabase.table("documents").insert({
#             "user_id": user_id,
#             "document_type": document_type,
#             "document_number": document_number,
#             "extracted_document_number": extracted_doc_number,
#             "document_image_url": document_url
#         }).execute()
        
#         # Update verification with duplicate check results
#         update_data = {
#             "document_number_match": doc_number_match,
#             "dob_match": dob_verification['match'],
#             "document_face_detected": face_detected,
#             "document_duplicate_check": document_duplicate_check,  # NEW
#             "ocr_data": {"raw_text": ocr_text[:500]}
#         }
        
#         if face_detected:
#             update_data["document_face_embedding"] = face_data['embedding']
#             update_data["document_face_confidence"] = face_data['confidence']
        
#         supabase.table("verifications").update(update_data).eq("user_id", user_id).execute()
        
#         print(f"\n✅ Document processing complete!")
        
#         return {
#             "success": True,
#             "document_url": document_url,
#             "extracted_doc_number": extracted_doc_number or "Not detected",
#             "doc_number_match": doc_number_match,
#             "dob_match": dob_verification['match'],
#             "face_detected": face_detected,
#             "face_confidence": face_data['confidence'] if face_detected else 0.0,
#             # NEW: Return duplicate check results
#             "duplicate_check": document_duplicate_check,
#             "warning": "Duplicate document face found!" if document_duplicate_check['is_duplicate'] else None
#         }
    
#     except Exception as e:
#         print(f"❌ Error: {e}")
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(status_code=400, detail=str(e))
@app.post("/api/documents/upload")
async def upload_document(
    user_id: str = Form(...),
    document_type: str = Form(...),
    document_number: str = Form(...),
    document_image: UploadFile = File(...),
    user_dob: str = Form(...)
):
    try:
        print(f"\n{'='*60}")
        print(f"Processing {document_type} for user: {user_id}")
        print(f"{'='*60}")
        
        image_bytes = await document_image.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # OCR extraction
        print("Running OCR...")
        ocr_text = extract_text_with_multiple_methods(image)
        extracted_doc_number = extract_document_number(ocr_text, document_type)
        extracted_dates = extract_date_of_birth(ocr_text)
        
        doc_number_match = verify_document_number(document_number, extracted_doc_number)
        dob_verification = verify_dob_with_retry(user_dob, extracted_dates)
        
        # Extract face from document
        print("\nExtracting face from document...")
        face_data = extract_face_from_image(image_bytes)
        face_detected = face_data is not None
        
        # Initialize duplicate check result
        document_duplicate_check = {
            'is_duplicate': False,
            'duplicate_count': 0,
            'matches': [],
            'total_compared': 0
        }
        
        # NEW: Update last activity (extends expiry)
        update_last_activity(user_id)
        
        # NEW: Check for duplicates ONLY if face was detected
        if face_detected:
            print("\n🔍 Checking for duplicate document faces...")
            document_duplicate_check = check_duplicate_user(
                face_data['embedding'], 
                'document',
                user_id  # Exclude current user from comparison
            )
            
            if document_duplicate_check['is_duplicate']:
                print(f"⚠️  ALERT: Found {document_duplicate_check['duplicate_count']} duplicate(s)!")
                # Continue processing but flag as duplicate
            else:
                print(f"✅ No duplicates found - document is unique")
        else:
            print("⚠️  No face detected in document - skipping duplicate check")
        
        # Upload to Supabase Storage
        print("\nUploading to Supabase storage...")
        file_path = f"{user_id}/{document_type}_{uuid.uuid4()}.jpg"
        supabase.storage.from_("document-images").upload(
            file_path, image_bytes, {"content-type": "image/jpeg"}
        )
        document_url = supabase.storage.from_("document-images").get_public_url(file_path)
        print(f"✅ Uploaded: {document_url}")
        
        # Save to documents table
        print("Saving document metadata...")
        supabase.table("documents").insert({
            "user_id": user_id,
            "document_type": document_type,
            "document_number": document_number,
            "extracted_document_number": extracted_doc_number,
            "document_image_url": document_url
        }).execute()
        
        # Prepare verification update data
        update_data = {
            "document_number_match": doc_number_match,
            "dob_match": dob_verification['match'],
            "document_face_detected": face_detected,
            "ocr_data": json.dumps({"raw_text": ocr_text[:500]})  # Store as JSON
        }
        
        # Add face data if detected
        if face_detected:
            update_data["document_face_embedding"] = face_data['embedding']
            update_data["document_face_confidence"] = float(face_data['confidence'])
            
            # Convert duplicate check to JSON-serializable format
            duplicate_check_json = {
                'is_duplicate': bool(document_duplicate_check.get('is_duplicate', False)),
                'duplicate_count': int(document_duplicate_check.get('duplicate_count', 0)),
                'total_compared': int(document_duplicate_check.get('total_compared', 0)),
                'total_filtered': int(document_duplicate_check.get('total_filtered', 0)),
                'matches': [
                    {
                        'user_id': str(match['user_id']),
                        'similarity_percentage': float(match['similarity_percentage']),
                        'comparison_type': str(match['comparison_type']),
                        'is_verified': bool(match.get('is_verified', False))
                    }
                    for match in document_duplicate_check.get('matches', [])
                ]
            }
            update_data["document_duplicate_check"] = json.dumps(duplicate_check_json)
        
        # Update verification table
        print("Updating verification record...")
        supabase.table("verifications").update(update_data).eq("user_id", user_id).execute()
        
        print(f"\n✅ Document processing complete!")
        
        return {
            "success": True,
            "document_url": document_url,
            "extracted_doc_number": extracted_doc_number or "Not detected",
            "doc_number_match": doc_number_match,
            "dob_match": dob_verification['match'],
            "face_detected": face_detected,
            "face_confidence": face_data['confidence'] if face_detected else 0.0,
            "duplicate_check": document_duplicate_check,
            "warning": "Duplicate document face found!" if document_duplicate_check.get('is_duplicate') else None
        }
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))



# @app.post("/api/images/upload-selfie")
# async def upload_selfie(
#     user_id: str = Form(...),
#     selfie_image: UploadFile = File(...)
# ):
#     """Upload selfie and extract face embedding"""
#     try:
#         image_bytes = await selfie_image.read()
        
#         # Extract face from selfie
#         face_data = extract_face_from_image(image_bytes)
        
#         if not face_data:
#             raise HTTPException(
#                 status_code=400,
#                 detail="No face detected in selfie. Please upload a clear photo."
#             )
        
#         # Upload to Supabase Storage: user_id/selfie_uuid.jpg
#         file_path = f"{user_id}/selfie_{uuid.uuid4()}.jpg"
        
#         supabase.storage.from_("selfie-images").upload(
#             file_path,
#             image_bytes,
#             {"content-type": "image/jpeg"}
#         )
        
#         selfie_url = supabase.storage.from_("selfie-images").get_public_url(file_path)
        
#         # Update verification with selfie embedding
#         supabase.table("verifications").update({
#             "selfie_image_url": selfie_url,
#             "selfie_face_embedding": face_data['embedding'],
#             "selfie_face_confidence": face_data['confidence']
#         }).eq("user_id", user_id).execute()
        
#         return {
#             "success": True,
#             "selfie_url": selfie_url,
#             "face_confidence": face_data['confidence']
#         }
    
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# @app.post("/api/images/upload-selfie")
# async def upload_selfie(
#     user_id: str = Form(...),
#     selfie_image: UploadFile = File(...)
# ):
#     try:
#         print(f"\n{'='*60}")
#         print(f"Processing selfie for user: {user_id}")
#         print(f"{'='*60}")
        
#         image_bytes = await selfie_image.read()
        
#         # Extract face from selfie
#         face_data = extract_face_from_image(image_bytes)
        
#         if not face_data:
#             raise HTTPException(
#                 status_code=400,
#                 detail="No face detected in selfie. Please upload a clear photo."
#             )
        
#         # NEW: Check for duplicates in selfie faces
#         print("\n🔍 Checking for duplicate selfie faces...")
#         selfie_duplicate_check = check_duplicate_user(
#             face_data['embedding'], 
#             'selfie'
#         )
        
#         if selfie_duplicate_check['is_duplicate']:
#             print(f"⚠️  ALERT: Found {selfie_duplicate_check['duplicate_count']} duplicate(s)!")
        
#         # Upload to Supabase Storage
#         file_path = f"{user_id}/selfie_{uuid.uuid4()}.jpg"
#         supabase.storage.from_("selfie-images").upload(
#             file_path, image_bytes, {"content-type": "image/jpeg"}
#         )
#         selfie_url = supabase.storage.from_("selfie-images").get_public_url(file_path)
        
#         # Update verification with selfie embedding and duplicate check
#         supabase.table("verifications").update({
#             "selfie_image_url": selfie_url,
#             "selfie_face_embedding": face_data['embedding'],
#             "selfie_face_confidence": face_data['confidence'],
#             "selfie_duplicate_check": selfie_duplicate_check  # NEW
#         }).eq("user_id", user_id).execute()
        
#         print(f"\n✅ Selfie processing complete!")
        
#         return {
#             "success": True,
#             "selfie_url": selfie_url,
#             "face_confidence": face_data['confidence'],
#             # NEW: Return duplicate check results
#             "duplicate_check": selfie_duplicate_check,
#             "warning": "Duplicate selfie face found!" if selfie_duplicate_check['is_duplicate'] else None
#         }
    
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
# @app.post("/api/images/upload-selfie")
# async def upload_selfie(
#     user_id: str = Form(...),
#     selfie_image: UploadFile = File(...)
# ):
#     try:
#         print(f"\n{'='*60}")
#         print(f"Processing selfie for user: {user_id}")
#         print(f"File: {selfie_image.filename}, Type: {selfie_image.content_type}")
#         print(f"{'='*60}")
        
#         image_bytes = await selfie_image.read()
#         print(f"Image size: {len(image_bytes)} bytes")
        
#         # Extract face from selfie
#         face_data = extract_face_from_image(image_bytes)
        
#         if not face_data:
#             error_msg = "No face detected in selfie. Please upload a clear photo with visible face."
#             print(f"❌ {error_msg}")
#             raise HTTPException(status_code=400, detail=error_msg)
        
#         print(f"✅ Face detected with confidence: {face_data['confidence']:.4f}")
        
#         # Check for duplicates
#         print("\n🔍 Checking for duplicate selfie faces...")
#         selfie_duplicate_check = check_duplicate_user(
#             face_data['embedding'], 
#             'selfie'
#         )
        
#         if selfie_duplicate_check['is_duplicate']:
#             print(f"⚠️  ALERT: Found {selfie_duplicate_check['duplicate_count']} duplicate(s)!")
#         else:
#             print(f"✅ No duplicates found - User is unique")
        
#         # Upload to Supabase Storage
#         file_path = f"{user_id}/selfie_{uuid.uuid4()}.jpg"
#         supabase.storage.from_("selfie-images").upload(
#             file_path, image_bytes, {"content-type": "image/jpeg"}
#         )
#         selfie_url = supabase.storage.from_("selfie-images").get_public_url(file_path)
        
#         # Update verification
#         supabase.table("verifications").update({
#             "selfie_image_url": selfie_url,
#             "selfie_face_embedding": face_data['embedding'],
#             "selfie_face_confidence": face_data['confidence'],
#             "selfie_duplicate_check": selfie_duplicate_check
#         }).eq("user_id", user_id).execute()
        
#         print(f"\n✅ Selfie processing complete!")
        
#         return {
#             "success": True,
#             "selfie_url": selfie_url,
#             "face_confidence": face_data['confidence'],
#             "duplicate_check": selfie_duplicate_check,
#             "warning": "Duplicate selfie face found!" if selfie_duplicate_check['is_duplicate'] else None
#         }
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"❌ Error in selfie upload: {e}")
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(status_code=400, detail=str(e))

# @app.post("/api/images/upload-selfie")
# async def upload_selfie(
#     user_id: str = Form(...),
#     selfie_image: UploadFile = File(...)
# ):
#     try:
#         print(f"\n{'='*60}")
#         print(f"Processing selfie for user: {user_id}")
#         print(f"{'='*60}")
        
#         image_bytes = await selfie_image.read()
        
#         # Extract face from selfie
#         face_data = extract_face_from_image(image_bytes)
        
#         if not face_data:
#             raise HTTPException(
#                 status_code=400,
#                 detail="No face detected in selfie. Please upload a clear photo."
#             )
        
#         # Check for duplicates
#         print("\n🔍 Checking for duplicate selfie faces...")
#         selfie_duplicate_check = check_duplicate_user(
#             face_data['embedding'], 
#             'selfie'
#         )
        
#         if selfie_duplicate_check['is_duplicate']:
#             print(f"⚠️  ALERT: Found {selfie_duplicate_check['duplicate_count']} duplicate(s)!")
#         else:
#             print(f"✅ No duplicates found - User is unique")
        
#         # NEW: Convert duplicate check to JSON-serializable format
#         duplicate_check_json = {
#             'is_duplicate': bool(selfie_duplicate_check.get('is_duplicate', False)),
#             'duplicate_count': int(selfie_duplicate_check.get('duplicate_count', 0)),
#             'total_compared': int(selfie_duplicate_check.get('total_compared', 0)),
#             'matches': [
#                 {
#                     'user_id': str(match['user_id']),
#                     'similarity_percentage': float(match['similarity_percentage']),
#                     'comparison_type': str(match['comparison_type'])
#                 }
#                 for match in selfie_duplicate_check.get('matches', [])
#             ]
#         }
        
#         print("Uploading to Supabase storage...")
#         # Upload to Supabase Storage
#         file_path = f"{user_id}/selfie_{uuid.uuid4()}.jpg"
#         supabase.storage.from_("selfie-images").upload(
#             file_path, image_bytes, {"content-type": "image/jpeg"}
#         )
#         selfie_url = supabase.storage.from_("selfie-images").get_public_url(file_path)
#         print(f"✅ Uploaded to: {selfie_url}")
        
#         print("Updating database...")
#         # Update verification with JSON-serialized data
#         supabase.table("verifications").update({
#             "selfie_image_url": selfie_url,
#             "selfie_face_embedding": face_data['embedding'],
#             "selfie_face_confidence": float(face_data['confidence']),
#             "selfie_duplicate_check": json.dumps(duplicate_check_json)  # Convert to JSON string
#         }).eq("user_id", user_id).execute()
        
#         print(f"\n✅ Selfie processing complete!")
        
#         return {
#             "success": True,
#             "selfie_url": selfie_url,
#             "face_confidence": face_data['confidence'],
#             "duplicate_check": duplicate_check_json,
#             "warning": "Duplicate selfie face found!" if duplicate_check_json['is_duplicate'] else None
#         }
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"❌ Error in selfie upload: {e}")
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(status_code=400, detail=str(e))
@app.post("/api/images/upload-selfie")
async def upload_selfie(
    user_id: str = Form(...),
    selfie_image: UploadFile = File(...)
):
    try:
        print(f"\n{'='*60}")
        print(f"Processing selfie for user: {user_id}")
        print(f"{'='*60}")
        
        image_bytes = await selfie_image.read()
        
        # Extract face from selfie
        print("Extracting face from selfie...")
        face_data = extract_face_from_image(image_bytes)
        
        if not face_data:
            raise HTTPException(
                status_code=400,
                detail="No face detected in selfie. Please upload a clear photo."
            )
        
        print(f"✅ Face detected with confidence: {face_data['confidence']:.4f}")
        
        # NEW: Update last activity (extends expiry by 7 days)
        update_last_activity(user_id)
        
        # Check for duplicates
        print("\n🔍 Checking for duplicate selfie faces...")
        selfie_duplicate_check = check_duplicate_user(
            face_data['embedding'], 
            'selfie',
            user_id  # NEW: Pass user_id to exclude self from comparison
        )
        
        if selfie_duplicate_check['is_duplicate']:
            print(f"⚠️  ALERT: Found {selfie_duplicate_check['duplicate_count']} duplicate(s)!")
        else:
            print(f"✅ No duplicates found - selfie is unique")
        
        # Convert duplicate check to JSON-serializable format
        duplicate_check_json = {
            'is_duplicate': bool(selfie_duplicate_check.get('is_duplicate', False)),
            'duplicate_count': int(selfie_duplicate_check.get('duplicate_count', 0)),
            'total_compared': int(selfie_duplicate_check.get('total_compared', 0)),
            'total_filtered': int(selfie_duplicate_check.get('total_filtered', 0)),  # NEW
            'matches': [
                {
                    'user_id': str(match['user_id']),
                    'similarity_percentage': float(match['similarity_percentage']),
                    'comparison_type': str(match['comparison_type']),
                    'is_verified': bool(match.get('is_verified', False))  # NEW
                }
                for match in selfie_duplicate_check.get('matches', [])
            ]
        }
        
        print("Uploading to Supabase storage...")
        # Upload to Supabase Storage
        file_path = f"{user_id}/selfie_{uuid.uuid4()}.jpg"
        supabase.storage.from_("selfie-images").upload(
            file_path, image_bytes, {"content-type": "image/jpeg"}
        )
        selfie_url = supabase.storage.from_("selfie-images").get_public_url(file_path)
        print(f"✅ Uploaded to: {selfie_url}")
        
        print("Updating database...")
        # Update verification with JSON-serialized data
        supabase.table("verifications").update({
            "selfie_image_url": selfie_url,
            "selfie_face_embedding": face_data['embedding'],
            "selfie_face_confidence": float(face_data['confidence']),
            "selfie_duplicate_check": json.dumps(duplicate_check_json)
        }).eq("user_id", user_id).execute()
        
        print(f"\n✅ Selfie processing complete!")
        
        return {
            "success": True,
            "selfie_url": selfie_url,
            "face_confidence": face_data['confidence'],
            "duplicate_check": duplicate_check_json,
            "warning": "Duplicate selfie face found!" if duplicate_check_json['is_duplicate'] else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in selfie upload: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

#upload_live_preview
@app.post("/api/admin/cleanup-expired")
async def cleanup_expired_users():
    """
    Clean up expired incomplete registrations (admin only)
    """
    try:
        current_time = datetime.now().isoformat()
        
        # Find expired users
        expired = supabase.table("verifications").select("user_id").lt(
            "expiry_date", current_time
        ).eq("is_fully_verified", False).execute()
        
        expired_count = len(expired.data)
        
        # Optional: Delete or mark as expired
        for user in expired.data:
            supabase.table("verifications").update({
                "registration_status": "expired"
            }).eq("user_id", user['user_id']).execute()
        
        return {
            "success": True,
            "expired_count": expired_count,
            "message": f"Marked {expired_count} registrations as expired"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# @app.post("/api/images/upload-live-preview")
# async def upload_live_preview(
#     user_id: str = Form(...),
#     live_image: UploadFile = File(...)
# ):
#     """Upload live preview and verify against document and selfie"""
#     try:
#         image_bytes = await live_image.read()
        
#         # Step 1: Check liveness
#         liveness_result = check_liveness(image_bytes)
        
#         if not liveness_result.get('passed', False):
#             return {
#                 "success": False,
#                 "error": "Liveness check failed - possible spoofing detected",
#                 "liveness": liveness_result
#             }
        
#         # Step 2: Extract face from live capture
#         live_face_data = extract_face_from_image(image_bytes)
        
#         if not live_face_data:
#             raise HTTPException(
#                 status_code=400,
#                 detail="No face detected in live capture"
#             )
        
#         # Step 3: Get stored embeddings from database
#         verification = supabase.table("verifications").select("*").eq("user_id", user_id).execute()
        
#         if not verification.data:
#             raise HTTPException(status_code=404, detail="Verification record not found")
        
#         ver_data = verification.data[0]
#         document_embedding = ver_data.get('document_face_embedding')
#         selfie_embedding = ver_data.get('selfie_face_embedding')
        
#         if not document_embedding or not selfie_embedding:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Document or selfie face not found. Please upload both first."
#             )
        
#         # Step 4: Compare live capture with document
#         doc_comparison = compare_face_embeddings(
#             document_embedding,
#             live_face_data['embedding']
#         )
        
#         # Step 5: Compare live capture with selfie
#         selfie_comparison = compare_face_embeddings(
#             selfie_embedding,
#             live_face_data['embedding']
#         )
        
#         # Step 6: Determine overall verification
#         verification_passed = all([
#             liveness_result.get('passed', False),
#             doc_comparison['match'],
#             selfie_comparison['match']
#         ])
        
#         avg_similarity = (doc_comparison['similarity_percentage'] + selfie_comparison['similarity_percentage']) / 2
        
#         # Upload live image
#         file_path = f"{user_id}/live_{uuid.uuid4()}.jpg"
        
#         supabase.storage.from_("live-preview-images").upload(
#             file_path,
#             image_bytes,
#             {"content-type": "image/jpeg"}
#         )
        
#         live_url = supabase.storage.from_("live-preview-images").get_public_url(file_path)
        
#         # Update verification record
#         supabase.table("verifications").update({
#             "live_preview_image_url": live_url,
#             "face_similarity_verified": verification_passed,
#             "face_similarity_percentage": avg_similarity,
#             "liveness_passed": liveness_result.get('passed', False),
#             "liveness_confidence": liveness_result.get('confidence', 0.0),
#             "verification_data": {
#                 "liveness": liveness_result,
#                 "document_comparison": doc_comparison,
#                 "selfie_comparison": selfie_comparison
#             }
#         }).eq("user_id", user_id).execute()
        
#         return {
#             "success": True,
#             "verification_passed": verification_passed,
#             "live_url": live_url,
#             "liveness": liveness_result,
#             "document_comparison": doc_comparison,
#             "selfie_comparison": selfie_comparison,
#             "overall_similarity": avg_similarity
#         }
    
#     except Exception as e:
#         print(f"Error in live preview: {e}")
#         raise HTTPException(status_code=400, detail=str(e))
# @app.post("/api/images/upload-live-preview")
# async def upload_live_preview(
#     user_id: str = Form(...),
#     live_image: UploadFile = File(...)
# ):
#     """Upload live preview and verify against document and selfie"""
#     try:
#         image_bytes = await live_image.read()
        
#         # Step 1: Check liveness
#         print(f"Checking liveness for user: {user_id}")
#         liveness_result = check_liveness(image_bytes)
#         print(f"Liveness result: {liveness_result}")
        
#         if not liveness_result.get('passed', False):
#             return {
#                 "success": False,
#                 "error": "Liveness check failed - possible spoofing detected",
#                 "liveness": liveness_result,
#                 "verification_passed": False
#             }
        
#         # Step 2: Extract face from live capture
#         print("Extracting face from live capture...")
#         live_face_data = extract_face_from_image(image_bytes)
        
#         if not live_face_data:
#             raise HTTPException(
#                 status_code=400,
#                 detail="No face detected in live capture"
#             )
        
#         print(f"Face detected with confidence: {live_face_data['confidence']}")
        
#         # Step 3: Get stored embeddings from database
#         print(f"Fetching verification data for user: {user_id}")
#         verification = supabase.table("verifications").select("*").eq("user_id", user_id).execute()
        
#         if not verification.data:
#             raise HTTPException(status_code=404, detail="Verification record not found")
        
#         ver_data = verification.data[0]
#         document_embedding = ver_data.get('document_face_embedding')
#         selfie_embedding = ver_data.get('selfie_face_embedding')
        
#         if not document_embedding or not selfie_embedding:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Document or selfie face not found. Please upload both first."
#             )
        
#         print("Comparing faces...")
        
#         # Step 4: Compare live capture with document
#         doc_comparison = compare_face_embeddings(
#             document_embedding,
#             live_face_data['embedding']
#         )
#         print(f"Document comparison: {doc_comparison}")
        
#         # Step 5: Compare live capture with selfie
#         selfie_comparison = compare_face_embeddings(
#             selfie_embedding,
#             live_face_data['embedding']
#         )
#         print(f"Selfie comparison: {selfie_comparison}")
        
#         # Step 6: Determine overall verification
#         verification_passed = bool(all([
#             liveness_result.get('passed', False),
#             doc_comparison.get('match', False),
#             selfie_comparison.get('match', False)
#         ]))
        
#         avg_similarity = float((
#             doc_comparison.get('similarity_percentage', 0) + 
#             selfie_comparison.get('similarity_percentage', 0)
#         ) / 2)
        
#         print(f"Verification passed: {verification_passed}, Avg similarity: {avg_similarity}")
        
#         # Upload live image
#         file_path = f"{user_id}/live_{uuid.uuid4()}.jpg"
        
#         supabase.storage.from_("live-preview-images").upload(
#             file_path,
#             image_bytes,
#             {"content-type": "image/jpeg"}
#         )
        
#         live_url = supabase.storage.from_("live-preview-images").get_public_url(file_path)
        
#         # Update verification record with proper type conversion
#         update_data = {
#             "live_preview_image_url": live_url,
#             "face_similarity_verified": verification_passed,
#             "face_similarity_percentage": avg_similarity,
#             "liveness_passed": bool(liveness_result.get('passed', False)),
#             "liveness_confidence": float(liveness_result.get('confidence', 0.0)),
#             "verification_data": {
#                 "liveness": {
#                     "success": bool(liveness_result.get('success', False)),
#                     "is_real": bool(liveness_result.get('is_real', False)),
#                     "confidence": float(liveness_result.get('confidence', 0.0)),
#                     "passed": bool(liveness_result.get('passed', False))
#                 },
#                 "document_comparison": {
#                     "match": bool(doc_comparison.get('match', False)),
#                     "similarity": float(doc_comparison.get('similarity', 0.0)),
#                     "similarity_percentage": float(doc_comparison.get('similarity_percentage', 0.0)),
#                     "threshold": float(doc_comparison.get('threshold', 0.0))
#                 },
#                 "selfie_comparison": {
#                     "match": bool(selfie_comparison.get('match', False)),
#                     "similarity": float(selfie_comparison.get('similarity', 0.0)),
#                     "similarity_percentage": float(selfie_comparison.get('similarity_percentage', 0.0)),
#                     "threshold": float(selfie_comparison.get('threshold', 0.0))
#                 }
#             }
#         }
        
#         print("Updating database...")
#         supabase.table("verifications").update(update_data).eq("user_id", user_id).execute()
        
#         # Return response with proper type conversion
#         return {
#             "success": True,
#             "verification_passed": bool(verification_passed),
#             "live_url": live_url,
#             "liveness": {
#                 "success": bool(liveness_result.get('success', False)),
#                 "is_real": bool(liveness_result.get('is_real', False)),
#                 "confidence": float(liveness_result.get('confidence', 0.0)),
#                 "passed": bool(liveness_result.get('passed', False))
#             },
#             "document_comparison": {
#                 "match": bool(doc_comparison.get('match', False)),
#                 "similarity_percentage": float(doc_comparison.get('similarity_percentage', 0.0))
#             },
#             "selfie_comparison": {
#                 "match": bool(selfie_comparison.get('match', False)),
#                 "similarity_percentage": float(selfie_comparison.get('similarity_percentage', 0.0))
#             },
#             "overall_similarity": float(avg_similarity)
#         }
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"Error in live preview: {e}")
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(status_code=400, detail=str(e))
# @app.post("/api/images/upload-live-preview")
# async def upload_live_preview(
#     user_id: str = Form(...),
#     live_image: UploadFile = File(...)
# ):
#     try:
#         print(f"\n{'='*60}")
#         print(f"Processing live capture for user: {user_id}")
#         print(f"{'='*60}")
        
#         image_bytes = await live_image.read()
        
#         # Step 1: Check liveness
#         print("Checking liveness...")
#         liveness_result = check_liveness(image_bytes)
        
#         if not liveness_result.get('passed', False):
#             return {
#                 "success": False,
#                 "error": "Liveness check failed - possible spoofing detected",
#                 "liveness": liveness_result,
#                 "verification_passed": False
#             }
        
#         # Step 2: Extract face from live capture
#         print("Extracting face from live capture...")
#         live_face_data = extract_face_from_image(image_bytes)
        
#         if not live_face_data:
#             raise HTTPException(status_code=400, detail="No face detected in live capture")
        
#         # NEW: Check for duplicates in live captures
#         print("\n🔍 Checking for duplicate live captures...")
#         live_duplicate_check = check_duplicate_user(
#             live_face_data['embedding'], 
#             'live'
#         )
        
#         if live_duplicate_check['is_duplicate']:
#             print(f"⚠️  ALERT: Found {live_duplicate_check['duplicate_count']} duplicate(s)!")
        
#         # Step 3: Get stored embeddings from database
#         verification = supabase.table("verifications").select("*").eq("user_id", user_id).execute()
        
#         if not verification.data:
#             raise HTTPException(status_code=404, detail="Verification record not found")
        
#         ver_data = verification.data[0]
#         document_embedding = ver_data.get('document_face_embedding')
#         selfie_embedding = ver_data.get('selfie_face_embedding')
        
#         if not document_embedding or not selfie_embedding:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Document or selfie face not found. Please upload both first."
#             )
        
#         # Step 4: Compare faces
#         print("Comparing faces...")
#         doc_comparison = compare_face_embeddings(document_embedding, live_face_data['embedding'])
#         selfie_comparison = compare_face_embeddings(selfie_embedding, live_face_data['embedding'])
        
#         # Step 5: Determine overall verification
#         # NEW: Check if duplicate was found in ANY of the checks
#         document_dup = ver_data.get('document_duplicate_check', {})
#         selfie_dup = ver_data.get('selfie_duplicate_check', {})
        
#         # If duplicate found in 2 or more checks, reject
#         duplicate_count = sum([
#             document_dup.get('is_duplicate', False),
#             selfie_dup.get('is_duplicate', False),
#             live_duplicate_check.get('is_duplicate', False)
#         ])
        
#         is_duplicate_user = duplicate_count >= 2
        
#         verification_passed = bool(all([
#             liveness_result.get('passed', False),
#             doc_comparison.get('match', False),
#             selfie_comparison.get('match', False),
#             not is_duplicate_user  # NEW: Reject if duplicate
#         ]))
        
#         avg_similarity = float((
#             doc_comparison.get('similarity_percentage', 0) + 
#             selfie_comparison.get('similarity_percentage', 0)
#         ) / 2)
        
#         # Upload live image
#         file_path = f"{user_id}/live_{uuid.uuid4()}.jpg"
#         supabase.storage.from_("live-preview-images").upload(
#             file_path, image_bytes, {"content-type": "image/jpeg"}
#         )
#         live_url = supabase.storage.from_("live-preview-images").get_public_url(file_path)
        
#         # Update verification record
#         update_data = {
#             "live_preview_image_url": live_url,
#             "live_face_embedding": live_face_data['embedding'],  # NEW: Store live embedding
#             "face_similarity_verified": verification_passed,
#             "face_similarity_percentage": avg_similarity,
#             "liveness_passed": bool(liveness_result.get('passed', False)),
#             "liveness_confidence": float(liveness_result.get('confidence', 0.0)),
#             "live_duplicate_check": live_duplicate_check,  # NEW
#             "is_duplicate_user": is_duplicate_user,  # NEW
#             "duplicate_detection_count": duplicate_count,  # NEW
#             "overall_status": "duplicate" if is_duplicate_user else ("verified" if verification_passed else "pending")
#         }
        
#         supabase.table("verifications").update(update_data).eq("user_id", user_id).execute()
        
#         print(f"\n✅ Live capture processing complete!")
#         print(f"Duplicate detection: {duplicate_count}/3 checks flagged")
        
#         return {
#             "success": True,
#             "verification_passed": verification_passed,
#             "live_url": live_url,
#             "liveness": liveness_result,
#             "document_comparison": doc_comparison,
#             "selfie_comparison": selfie_comparison,
#             "overall_similarity": avg_similarity,
#             # NEW: Duplicate detection results
#             "duplicate_detection": {
#                 "is_duplicate": is_duplicate_user,
#                 "checks_flagged": duplicate_count,
#                 "document_duplicate": document_dup.get('is_duplicate', False),
#                 "selfie_duplicate": selfie_dup.get('is_duplicate', False),
#                 "live_duplicate": live_duplicate_check.get('is_duplicate', False),
#                 "matching_users": live_duplicate_check.get('matches', [])
#             },
#             "rejection_reason": "Duplicate user detected" if is_duplicate_user else None
#         }
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"Error in live preview: {e}")
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(status_code=400, detail=str(e))
@app.post("/api/images/upload-live-preview")
async def upload_live_preview(
    user_id: str = Form(...),
    live_image: UploadFile = File(...)
):
    try:
        print(f"\n{'='*60}")
        print(f"Processing live capture for user: {user_id}")
        print(f"{'='*60}")
        
        image_bytes = await live_image.read()
        
        # Step 1: Check liveness
        print("Checking liveness...")
        liveness_result = check_liveness(image_bytes)
        
        if not liveness_result.get('passed', False):
            return {
                "success": False,
                "error": "Liveness check failed - possible spoofing detected",
                "liveness": liveness_result,
                "verification_passed": False
            }
        
        # Step 2: Extract face from live capture
        print("Extracting face from live capture...")
        live_face_data = extract_face_from_image(image_bytes)
        
        if not live_face_data:
            raise HTTPException(status_code=400, detail="No face detected in live capture")
        
        print(f"✅ Face detected with confidence: {live_face_data['confidence']:.4f}")
        
        # NEW: Update last activity (extends expiry)
        update_last_activity(user_id)
        
        # Step 3: Get stored embeddings from database FIRST (before duplicate check)
        print("\nFetching stored verification data...")
        verification = supabase.table("verifications").select("*").eq("user_id", user_id).execute()
        
        if not verification.data:
            raise HTTPException(status_code=404, detail="Verification record not found")
        
        ver_data = verification.data[0]
        document_embedding = ver_data.get('document_face_embedding')
        selfie_embedding = ver_data.get('selfie_face_embedding')
        
        if not document_embedding or not selfie_embedding:
            raise HTTPException(
                status_code=400,
                detail="Document or selfie face not found. Please upload both first."
            )
        
        # Step 4: Check for duplicates in live captures
        print("\n🔍 Checking for duplicate live captures...")
        live_duplicate_check = check_duplicate_user(
            live_face_data['embedding'], 
            'live',
            user_id  # NEW: Exclude current user from comparison
        )
        
        if live_duplicate_check['is_duplicate']:
            print(f"⚠️  ALERT: Found {live_duplicate_check['duplicate_count']} duplicate(s)!")
        else:
            print(f"✅ No duplicates found - live capture is unique")
        
        # Step 5: Compare faces
        print("\nComparing faces with stored embeddings...")
        doc_comparison = compare_face_embeddings(document_embedding, live_face_data['embedding'])
        selfie_comparison = compare_face_embeddings(selfie_embedding, live_face_data['embedding'])
        
        print(f"Document vs Live: {doc_comparison['similarity_percentage']:.2f}% - {'✅ Match' if doc_comparison['match'] else '❌ No Match'}")
        print(f"Selfie vs Live: {selfie_comparison['similarity_percentage']:.2f}% - {'✅ Match' if selfie_comparison['match'] else '❌ No Match'}")
        
        # Step 6: Parse previous duplicate checks (they are JSON strings)
        document_dup = ver_data.get('document_duplicate_check')
        selfie_dup = ver_data.get('selfie_duplicate_check')
        
        # NEW: Parse JSON strings to dicts
        if isinstance(document_dup, str):
            try:
                document_dup = json.loads(document_dup)
            except:
                document_dup = {}
        elif document_dup is None:
            document_dup = {}
        
        if isinstance(selfie_dup, str):
            try:
                selfie_dup = json.loads(selfie_dup)
            except:
                selfie_dup = {}
        elif selfie_dup is None:
            selfie_dup = {}
        
        # Step 7: Calculate duplicate count (2 or more = duplicate user)
        duplicate_count = sum([
            bool(document_dup.get('is_duplicate', False)),
            bool(selfie_dup.get('is_duplicate', False)),
            bool(live_duplicate_check.get('is_duplicate', False))
        ])
        
        is_duplicate_user = duplicate_count >= 2
        
        print(f"\nDuplicate Detection Summary:")
        print(f"  Document: {'❌ Duplicate' if document_dup.get('is_duplicate') else '✅ Unique'}")
        print(f"  Selfie: {'❌ Duplicate' if selfie_dup.get('is_duplicate') else '✅ Unique'}")
        print(f"  Live: {'❌ Duplicate' if live_duplicate_check.get('is_duplicate') else '✅ Unique'}")
        print(f"  Total Flagged: {duplicate_count}/3")
        print(f"  Final Decision: {'⛔ DUPLICATE USER' if is_duplicate_user else '✅ UNIQUE USER'}")
        
        # Step 8: Determine overall verification
        verification_passed = bool(all([
            liveness_result.get('passed', False),
            doc_comparison.get('match', False),
            selfie_comparison.get('match', False),
            not is_duplicate_user
        ]))
        
        avg_similarity = float((
            doc_comparison.get('similarity_percentage', 0) + 
            selfie_comparison.get('similarity_percentage', 0)
        ) / 2)
        
        # Step 9: Upload live image
        print("\nUploading live capture to storage...")
        file_path = f"{user_id}/live_{uuid.uuid4()}.jpg"
        supabase.storage.from_("live-preview-images").upload(
            file_path, image_bytes, {"content-type": "image/jpeg"}
        )
        live_url = supabase.storage.from_("live-preview-images").get_public_url(file_path)
        print(f"✅ Uploaded to: {live_url}")
        
        # Step 10: Convert live duplicate check to JSON
        live_duplicate_json = {
            'is_duplicate': bool(live_duplicate_check.get('is_duplicate', False)),
            'duplicate_count': int(live_duplicate_check.get('duplicate_count', 0)),
            'total_compared': int(live_duplicate_check.get('total_compared', 0)),
            'total_filtered': int(live_duplicate_check.get('total_filtered', 0)),
            'matches': [
                {
                    'user_id': str(match['user_id']),
                    'similarity_percentage': float(match['similarity_percentage']),
                    'comparison_type': str(match['comparison_type']),
                    'is_verified': bool(match.get('is_verified', False))
                }
                for match in live_duplicate_check.get('matches', [])
            ]
        }
        
        # Step 11: Update verification record
        print("\nUpdating verification record...")
        update_data = {
            "live_preview_image_url": live_url,
            "live_face_embedding": live_face_data['embedding'],
            "face_similarity_verified": verification_passed,
            "face_similarity_percentage": avg_similarity,
            "liveness_passed": bool(liveness_result.get('passed', False)),
            "liveness_confidence": float(liveness_result.get('confidence', 0.0)),
            "live_duplicate_check": json.dumps(live_duplicate_json),
            "is_duplicate_user": is_duplicate_user,
            "duplicate_detection_count": duplicate_count,
            "overall_status": "duplicate" if is_duplicate_user else ("verified" if verification_passed else "pending")
        }
        
        supabase.table("verifications").update(update_data).eq("user_id", user_id).execute()
        
        # Step 12: If verification passed and not duplicate, mark as fully verified
        if verification_passed and not is_duplicate_user:
            mark_as_verified(user_id)
            print("🎉 User registration complete - marked as fully verified!")
        
        print(f"\n✅ Live capture processing complete!")
        
        return {
            "success": True,
            "verification_passed": verification_passed,
            "live_url": live_url,
            "liveness": liveness_result,
            "document_comparison": doc_comparison,
            "selfie_comparison": selfie_comparison,
            "overall_similarity": avg_similarity,
            "duplicate_detection": {
                "is_duplicate": is_duplicate_user,
                "checks_flagged": duplicate_count,
                "document_duplicate": document_dup.get('is_duplicate', False),
                "selfie_duplicate": selfie_dup.get('is_duplicate', False),
                "live_duplicate": live_duplicate_check.get('is_duplicate', False),
                "matching_users": live_duplicate_check.get('matches', [])
            },
            "rejection_reason": "Duplicate user detected" if is_duplicate_user else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in live preview: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/biometric/upload")
async def upload_biometric(
    user_id: str = Form(...),
    biometric_image: UploadFile = File(...)
):
    """Upload biometric data"""
    try:
        image_bytes = await biometric_image.read()
        
        # Upload to Supabase: user_id/biometric_uuid.jpg
        file_path = f"{user_id}/biometric_{uuid.uuid4()}.jpg"
        
        supabase.storage.from_("biometric-images").upload(
            file_path,
            image_bytes,
            {"content-type": "image/jpeg"}
        )
        
        biometric_url = supabase.storage.from_("biometric-images").get_public_url(file_path)
        
        supabase.table("verifications").update({
            "biometric_image_url": biometric_url,
            "biometric_verified": True
        }).eq("user_id", user_id).execute()
        
        return {"success": True, "biometric_url": biometric_url}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/verification/status/{user_id}")
async def get_verification_status(user_id: str):
    """Get complete verification status"""
    try:
        verification = supabase.table("verifications").select("*").eq("user_id", user_id).execute()
        
        if not verification.data:
            raise HTTPException(status_code=404, detail="Verification not found")
        
        return {"success": True, "verification": verification.data[0]}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/users/lookup-by-email")
async def lookup_user_by_email(email: str = Form(...)):
    """Look up user by email"""
    try:
        user_response = supabase.table("users").select("*").eq("email", email).execute()
        
        if not user_response.data or len(user_response.data) == 0:
            raise HTTPException(status_code=404, detail="No user found with this email address")
        
        user = user_response.data[0]
        user_id = user['id']
        
        verification_response = supabase.table("verifications").select("*").eq("user_id", user_id).execute()
        verification = verification_response.data[0] if verification_response.data else None
        
        steps_completed = {
            "personal_info": True,
            "document_uploaded": verification and verification.get('document_number_match') is not None,
            "selfie_uploaded": verification and verification.get('selfie_image_url') is not None,
            "biometric_uploaded": verification and verification.get('biometric_image_url') is not None,
            "face_verified": verification and verification.get('face_similarity_verified') is not None
        }
        
        return {
            "success": True,
            "user_id": user_id,
            "user_data": {
                "first_name": user['first_name'],
                "last_name": user['last_name'],
                "email": user['email'],
                "date_of_birth": user['date_of_birth']
            },
            "verification_status": verification,
            "steps_completed": steps_completed,
            "is_fully_verified": all(steps_completed.values())
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
import tempfile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
build_path = r"C:\Users\sayan\OneDrive\Desktop\fai authx\frontend\build"
if os.path.exists(build_path):
    print(f"✅ Serving React frontend from: {build_path}")
    
    # Mount static files (CSS, JS, images)
    app.mount("/static", StaticFiles(directory=f"{build_path}/static"), name="static")
    
    # Serve React app for all non-API routes
    @app.get("/", include_in_schema=False)
    async def serve_home():
        return FileResponse(f"{build_path}/index.html")
    
    @app.get("/about", include_in_schema=False)
    async def serve_about():
        return FileResponse(f"{build_path}/index.html")
    
    @app.get("/verification-status", include_in_schema=False)
    async def serve_status():
        return FileResponse(f"{build_path}/index.html")
else:
    print(f"⚠️  Frontend build not found at: {build_path}")
    print("   Run: cd frontend && npm run build")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
