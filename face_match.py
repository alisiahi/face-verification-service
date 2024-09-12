# face_match.py

import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
import requests
from io import BytesIO
from PIL import Image
from fastapi import HTTPException

# Initialize FaceAnalysis
face_analyzer = FaceAnalysis(providers=['CPUExecutionProvider'])
face_analyzer.prepare(ctx_id=0, det_size=(640, 640))

def load_image_from_url(url):
    print(f"[INFO] Fetching image from URL: {url}")
    try:
        response = requests.get(url)
        print(f"[INFO] Response status code for {url}: {response.status_code}")
        
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img = np.array(img)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            print(f"[INFO] Image loaded successfully from: {url}")
            return img
        else:
            print(f"[ERROR] Failed to load image from: {url}, Status code: {response.status_code}")
            raise HTTPException(status_code=400, detail=f"Image could not be retrieved from {url}")
    except Exception as e:
        print(f"[ERROR] Exception occurred while fetching image: {e}")
        raise HTTPException(status_code=400, detail="Image could not be retrieved.")


def get_face_embedding(image: np.ndarray):
    print(f"[INFO] Detecting face in the image.")
    faces = face_analyzer.get(image)
    if len(faces) == 0:
        print(f"[WARNING] No faces detected.")
        return None
    print(f"[INFO] Face detected. Embedding generated.")
    return faces[0].embedding

def cosine_similarity(a, b):
    print(f"[INFO] Calculating cosine similarity.")
    similarity = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    print(f"[INFO] Cosine similarity result: {similarity}")
    return similarity


def compare_faces(id_photo_url: str, selfie_photo_url: str):
    print(f"[INFO] Initiating face comparison.")
    print(f"[INFO] Fetching ID photo from: {id_photo_url}")
    print(f"[INFO] Fetching selfie photo from: {selfie_photo_url}")
    id_image = load_image_from_url(id_photo_url)
    selfie_image = load_image_from_url(selfie_photo_url)

    print(f"[INFO] Images fetched. Generating embeddings.")
    id_embedding = get_face_embedding(id_image)
    selfie_embedding = get_face_embedding(selfie_image)

    if id_embedding is None or selfie_embedding is None:
        print(f"[ERROR] Face not detected in one or both images.")
        return {"match": False, "message": "Face not detected in one or both images"}

    similarity = cosine_similarity(id_embedding, selfie_embedding)

    if similarity > 0.5:
        print(f"[INFO] Faces match with similarity: {similarity:.2f}")
        return {"match": True, "message": f"Face match! Similarity: {similarity:.2f}"}
    else:
        print(f"[INFO] Faces do not match. Similarity: {similarity:.2f}")
        return {"match": False, "message": f"Face mismatch. Similarity: {similarity:.2f}"}


