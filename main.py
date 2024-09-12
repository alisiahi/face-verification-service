from fastapi import FastAPI, HTTPException, BackgroundTasks, Header, Depends, Request
from pydantic import BaseModel
import asyncio
import httpx
import os
from fastapi.security import APIKeyHeader
from fastapi import Security
from face_match import compare_faces

app = FastAPI()

# Environment variables
NEXTJS_API_KEY = os.getenv("NEXTJS_API_KEY")
FASTAPI_API_KEY = os.getenv("FASTAPI_API_KEY")
NEXTJS_APP_URL = os.getenv("NEXTJS_APP_URL")

# API key security
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != NEXTJS_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

class VerificationRequest(BaseModel):
    userId: str
    selfie_url: str
    id_url: str

# main.py

from fastapi import FastAPI, HTTPException, BackgroundTasks, Header, Depends, Request
from pydantic import BaseModel
import httpx
import os
from fastapi.security import APIKeyHeader
from fastapi import Security
from face_match import compare_faces  # Import the face match function

app = FastAPI()

# Environment variables
NEXTJS_API_KEY = os.getenv("NEXTJS_API_KEY")
FASTAPI_API_KEY = os.getenv("FASTAPI_API_KEY")
NEXTJS_APP_URL = os.getenv("NEXTJS_APP_URL")

# API key security
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != NEXTJS_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

class VerificationRequest(BaseModel):
    userId: str
    selfie_url: str
    id_url: str

async def send_verification_result(userId: str, id_url: str, selfie_url: str):
    try:
        print(f"[INFO] Starting face match for user: {userId}")
        face_match_result = compare_faces(id_url, selfie_url)
        print(f"[INFO] Face match result for user {userId}: {face_match_result}")

        # Send the result back to the Next.js app
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{NEXTJS_APP_URL}/api/verification-webhook",
                json={"userId": userId, "isVerified": face_match_result["match"]},
                headers={"X-API-Key": FASTAPI_API_KEY}
            )
            print(f"[INFO] Verification result sent. Status code: {response.status_code}")

    except Exception as e:
        print(f"[ERROR] Failed to process face match for user {userId}: {e}")
        # You can't raise an HTTPException here because the response has already been sent


@app.post("/verify")
async def verify(request: Request, verification_request: VerificationRequest, background_tasks: BackgroundTasks, api_key: str = Depends(verify_api_key)):
    try:
        # Print all request headers
        
        
        print(f"Received verification request for user {verification_request.userId}")
        
        
        # Schedule the background task to perform face match and send the result
        background_tasks.add_task(send_verification_result, verification_request.userId, verification_request.selfie_url, verification_request.id_url)
        
        return {
            "success": True,
            "message": "Data has been received successfully. Verification result will be processed."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

@app.get("/users")
async def read_users():
    return {"users": ["Alice", "Bob", "Charlie"]}