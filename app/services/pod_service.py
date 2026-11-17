import hmac
import os
import uuid
from datetime import datetime
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException

POD_UPLOAD_DIR = "/data/antigravity/smartfleet_backend/app/uploads/pod"

def verify_pod_otp(expected_otp: str, candidate_otp: str) -> bool:
    """
    Timing-attack safe comparison of handover OTP using hmac.compare_digest.
    """
    if not expected_otp or not candidate_otp:
        return False
    # Normalize both strings
    return hmac.compare_digest(str(expected_otp).strip(), str(candidate_otp).strip())

async def save_pod_photo(trip_id: str, photo: UploadFile) -> str:
    """
    Validate MIME type, save uploaded cargo photo file, and return public relative URL.
    """
    allowed_content_types = {"image/jpeg", "image/png", "image/webp"}
    if photo.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid photo type {photo.content_type}. Allowed types: JPEG, PNG, WebP"
        )

    os.makedirs(POD_UPLOAD_DIR, exist_ok=True)
    ext = ".jpg" if "jpeg" in photo.content_type else (".png" if "png" in photo.content_type else ".webp")
    filename = f"pod_{trip_id}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(POD_UPLOAD_DIR, filename)

    content = await photo.read()
    # Check max size (10 MB)
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Photo file exceeds 10 MB limit")

    with open(filepath, "wb") as f:
        f.write(content)

    return f"/uploads/pod/{filename}"

def save_signature_svg(trip_id: str, svg_raw: str) -> str:
    """
    Validate and save recipient SVG vector signature to file or return stored SVG.
    """
    if not svg_raw or "<svg" not in svg_raw.lower():
        # If it is raw path data or standard string, wrap or save safely
        if not svg_raw.strip():
            raise HTTPException(status_code=400, detail="Signature data cannot be empty")

    os.makedirs(POD_UPLOAD_DIR, exist_ok=True)
    filename = f"sig_{trip_id}_{uuid.uuid4().hex[:8]}.svg"
    filepath = os.path.join(POD_UPLOAD_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg_raw)

    return f"/uploads/pod/{filename}"
