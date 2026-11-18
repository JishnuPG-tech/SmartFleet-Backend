import os
import hashlib
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.database import get_db
from app.models.config import FleetConfig

router = APIRouter(prefix="/app", tags=["In-App Enterprise Auto-Updater"])

APK_UPLOAD_DIR = os.path.join(settings.UPLOAD_DIR, "apks")
os.makedirs(APK_UPLOAD_DIR, exist_ok=True)

CONFIG_KEY = "app_update_info"

DEFAULT_UPDATE_DATA: Dict[str, Any] = {
    "latest_version_name": "2.1.0",
    "latest_version_code": 2,
    "min_supported_version_code": 1,
    "download_url": "https://jishnupg-opencode-cli.hf.space/preview/8000/uploads/apks/SmartFleet-latest.apk",
    "apk_filename": "SmartFleet-latest.apk",
    "apk_size_bytes": 181400000,
    "checksum_sha256": None,
    "release_notes": [
        "Driver lifecycle state management: Standby, Active, and Breakdown SOS",
        "NH-66 real-time GPS telemetry tracking and route monitoring",
        "Offline-first waybill caching with instant cloud synchronization",
        "Verified SHA-256 binary package delivery via in-app channel"
    ],
    "is_mandatory": False,
    "published_at": "2026-11-18T10:00:00Z"
}

class AppUpdateCheckResponse(BaseModel):
    update_available: bool = Field(..., description="True if a newer version is available")
    is_mandatory: bool = Field(..., description="True if current version is below minimum supported version")
    latest_version_name: str
    latest_version_code: int
    min_supported_version_code: int
    download_url: str
    apk_size_bytes: int
    checksum_sha256: Optional[str] = None
    release_notes: List[str]
    published_at: str

class PublishUpdateRequest(BaseModel):
    latest_version_name: str
    latest_version_code: int
    min_supported_version_code: int = 1
    download_url: Optional[str] = None
    release_notes: List[str]
    is_mandatory: bool = False

async def _get_or_create_update_config(db: AsyncSession) -> FleetConfig:
    result = await db.execute(select(FleetConfig).filter(FleetConfig.key == CONFIG_KEY))
    cfg = result.scalars().first()
    if not cfg:
        try:
            cfg = FleetConfig(key=CONFIG_KEY, data=DEFAULT_UPDATE_DATA, version=1)
            db.add(cfg)
            await db.commit()
            await db.refresh(cfg)
        except Exception:
            await db.rollback()
            result = await db.execute(select(FleetConfig).filter(FleetConfig.key == CONFIG_KEY))
            cfg = result.scalars().first()
    return cfg

@router.get("/check-update", response_model=AppUpdateCheckResponse)
async def check_update(
    current_version_code: int = Query(1, description="Client versionCode"),
    current_version_name: Optional[str] = Query(None, description="Client versionName"),
    platform: str = Query("android", description="Platform identifier"),
    db: AsyncSession = Depends(get_db)
):
    cfg = await _get_or_create_update_config(db)
    data = dict(cfg.data)

    latest_code = int(data.get("latest_version_code", 2))
    min_code = int(data.get("min_supported_version_code", 1))
    is_mandatory_flag = bool(data.get("is_mandatory", False))

    update_available = current_version_code < latest_code
    is_mandatory = update_available and (current_version_code < min_code or is_mandatory_flag)

    download_url = data.get("download_url") or "https://jishnupg-opencode-cli.hf.space/preview/8000/uploads/apks/SmartFleet-latest.apk"
    if download_url.startswith("/"):
        download_url = f"https://jishnupg-opencode-cli.hf.space/preview/8000{download_url}"

    return AppUpdateCheckResponse(
        update_available=update_available,
        is_mandatory=is_mandatory,
        latest_version_name=str(data.get("latest_version_name", "2.1.0")),
        latest_version_code=latest_code,
        min_supported_version_code=min_code,
        download_url=download_url,
        apk_size_bytes=int(data.get("apk_size_bytes", 0)),
        checksum_sha256=data.get("checksum_sha256"),
        release_notes=data.get("release_notes", []),
        published_at=str(data.get("published_at", datetime.now(timezone.utc).isoformat()))
    )

@router.post("/publish-update")
async def publish_update(
    version_name: str = Form(..., description="Version name e.g. 2.1.0"),
    version_code: int = Form(..., description="Version code e.g. 2"),
    min_supported_version_code: int = Form(1, description="Minimum supported version code"),
    is_mandatory: bool = Form(False, description="Enforce mandatory update lock"),
    release_notes_raw: str = Form(..., description="Release notes separated by newlines or semicolons"),
    apk_file: Optional[UploadFile] = File(None, description="APK binary file"),
    external_download_url: Optional[str] = Form(None, description="Direct download URL if not uploading file"),
    db: AsyncSession = Depends(get_db)
):
    cfg = await _get_or_create_update_config(db)
    data = dict(cfg.data)

    notes = [line.strip("-•* 	") for line in release_notes_raw.replace(";", chr(10)).splitlines() if line.strip()]
    if not notes:
        notes = ["General performance improvements and stability updates."]

    download_url = external_download_url
    apk_size = 0
    sha256_hash = None

    if apk_file and apk_file.filename:
        filename = f"SmartFleet-v{version_name}-code{version_code}.apk"
        save_path = os.path.join(APK_UPLOAD_DIR, filename)
        latest_symlink_target = os.path.join(APK_UPLOAD_DIR, "SmartFleet-latest.apk")

        hasher = hashlib.sha256()
        with open(save_path, 'wb') as f:
            while True:
                chunk = await apk_file.read(1024 * 1024)
                if not chunk:
                    break
                hasher.update(chunk)
                f.write(chunk)
        
        apk_size = os.path.getsize(save_path)
        sha256_hash = hasher.hexdigest()

        try:
            if os.path.islink(latest_symlink_target) or os.path.exists(latest_symlink_target):
                os.remove(latest_symlink_target)
            os.link(save_path, latest_symlink_target)
        except Exception:
            import shutil
            shutil.copy2(save_path, latest_symlink_target)

        download_url = f"https://jishnupg-opencode-cli.hf.space/preview/8000/uploads/apks/{filename}"
        data["apk_filename"] = filename

    elif not download_url:
        download_url = data.get("download_url", "https://jishnupg-opencode-cli.hf.space/preview/8000/uploads/apks/SmartFleet-latest.apk")

    now_iso = datetime.now(timezone.utc).isoformat()
    data.update({
        "latest_version_name": version_name,
        "latest_version_code": version_code,
        "min_supported_version_code": min_supported_version_code,
        "download_url": download_url,
        "release_notes": notes,
        "is_mandatory": is_mandatory,
        "published_at": now_iso
    })
    if apk_size > 0:
        data["apk_size_bytes"] = apk_size
    if sha256_hash:
        data["checksum_sha256"] = sha256_hash

    cfg.data = data
    cfg.version += 1
    db.add(cfg)
    await db.commit()
    await db.refresh(cfg)

    return {
        "status": "success",
        "message": f"Successfully published release v{version_name} (code {version_code})",
        "update_info": cfg.data
    }

@router.get("/download-latest")
async def download_latest_apk():
    latest_path = os.path.join(APK_UPLOAD_DIR, "SmartFleet-latest.apk")
    if os.path.exists(latest_path):
        return FileResponse(
            path=latest_path,
            filename="SmartFleet-latest.apk",
            media_type="application/vnd.android.package-archive"
        )
    return RedirectResponse(url="https://jishnupg-opencode-cli.hf.space/preview/8000/uploads/apks/SmartFleet-latest.apk")
