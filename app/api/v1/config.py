from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.config import FleetConfig
from app.schemas.config import (
    FleetMetadataResponse,
    CargoAddRequest,
    WeightAddRequest,
    HubAddRequest,
    BroadcastRequest,
    BroadcastBanner,
)

router = APIRouter(prefix="/config", tags=["Dynamic Configuration & SDUI"])

DEFAULT_METADATA: Dict[str, Any] = {
    "cargos": [
        "Industrial Steel Coils",
        "Container Freight (Electronics & Spices)",
        "Cement Sacks & TMT Steel Bars",
        "Bulk Polymer Granules",
        "Automotive Spare Parts",
        "Food Grains & Rice Sacks",
        "Timber & Wood Pulp",
        "Petroleum & Chemical Drums",
        "FMCG Packaged Goods",
        "Construction Aggregates & Sand",
        "Ceramic Tiles & Sanitaryware",
    ],
    "weights": [
        {"label": "5.0 Tons (Light Commercial)", "val": 5.0},
        {"label": "10.0 Tons (6-Wheel Rigid)", "val": 10.0},
        {"label": "15.0 Tons (10-Wheel Medium)", "val": 15.0},
        {"label": "18.5 Tons (Multi-Axle Cargo)", "val": 18.5},
        {"label": "22.0 Tons (Heavy Multi-Axle)", "val": 22.0},
        {"label": "25.0 Tons (Standard 12-Wheel)", "val": 25.0},
        {"label": "28.0 Tons (14-Wheel Heavy)", "val": 28.0},
        {"label": "31.0 Tons (Multi-Axle Tipper)", "val": 31.0},
        {"label": "35.0 Tons (Heavy Tipper)", "val": 35.0},
        {"label": "40.0 Tons (Trailer Haulage)", "val": 40.0},
    ],
    "hubs": [
        {"city": "Kochi", "code": "COK", "name": "Kochi Port & Willingdon Yard", "lat": 9.9312, "lng": 76.2673},
        {"city": "Kozhikode", "code": "CCJ", "name": "Kozhikode Bypass Industrial Yard", "lat": 11.2588, "lng": 75.7804},
        {"city": "Kannur", "code": "CNN", "name": "Kannur New Cargo Terminal", "lat": 11.8745, "lng": 75.3704},
        {"city": "Trivandrum", "code": "TRV", "name": "Trivandrum Petro Hub", "lat": 8.5241, "lng": 76.9366},
        {"city": "Palakkad", "code": "PGT", "name": "KINFRA Mega Food & Logistics Park", "lat": 10.7867, "lng": 76.6548},
    ],
    "driver_allowance_default": 1500,
    "system_status": "operational",
    "notice_banner": None,
    "version": 1,
}

CONFIG_KEY = "trip_presets"

async def _get_or_create_config(db: AsyncSession) -> FleetConfig:
    result = await db.execute(select(FleetConfig).filter(FleetConfig.key == CONFIG_KEY))
    cfg = result.scalars().first()
    if not cfg:
        cfg = FleetConfig(key=CONFIG_KEY, data=DEFAULT_METADATA, version=1)
        db.add(cfg)
        await db.commit()
        await db.refresh(cfg)
    return cfg

@router.get("/metadata", response_model=FleetMetadataResponse)
async def get_metadata(db: AsyncSession = Depends(get_db)):
    """Fetch active fleet configuration (cargos, weights, hubs, notices) with 0-second sync."""
    cfg = await _get_or_create_config(db)
    data = dict(cfg.data)
    data["version"] = cfg.version
    return data

@router.put("/metadata", response_model=FleetMetadataResponse)
async def update_metadata(payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    """Update full fleet metadata configuration."""
    cfg = await _get_or_create_config(db)
    current_data = dict(cfg.data)
    current_data.update(payload)
    cfg.data = current_data
    cfg.version += 1
    db.add(cfg)
    await db.commit()
    await db.refresh(cfg)
    resp = dict(cfg.data)
    resp["version"] = cfg.version
    return resp

# CARGO OPERATIONS
@router.post("/cargo")
async def add_cargo(payload: CargoAddRequest, db: AsyncSession = Depends(get_db)):
    cfg = await _get_or_create_config(db)
    data = dict(cfg.data)
    cargos = list(data.get("cargos", []))
    if payload.name not in cargos:
        cargos.append(payload.name)
        data["cargos"] = cargos
        cfg.data = data
        cfg.version += 1
        db.add(cfg)
        await db.commit()
    return {"ok": True, "cargos": data["cargos"], "version": cfg.version}

@router.delete("/cargo/{cargo_name}")
async def delete_cargo(cargo_name: str, db: AsyncSession = Depends(get_db)):
    cfg = await _get_or_create_config(db)
    data = dict(cfg.data)
    cargos = [c for c in data.get("cargos", []) if c != cargo_name]
    data["cargos"] = cargos
    cfg.data = data
    cfg.version += 1
    db.add(cfg)
    await db.commit()
    return {"ok": True, "cargos": data["cargos"], "version": cfg.version}

# WEIGHT OPERATIONS
@router.post("/weight")
async def add_weight(payload: WeightAddRequest, db: AsyncSession = Depends(get_db)):
    cfg = await _get_or_create_config(db)
    data = dict(cfg.data)
    weights = list(data.get("weights", []))
    # Replace if exists or append
    weights = [w for w in weights if abs(float(w.get("val", 0)) - payload.val) > 0.01]
    weights.append({"label": payload.label, "val": payload.val})
    weights.sort(key=lambda x: float(x.get("val", 0)))
    data["weights"] = weights
    cfg.data = data
    cfg.version += 1
    db.add(cfg)
    await db.commit()
    return {"ok": True, "weights": data["weights"], "version": cfg.version}

@router.delete("/weight/{val}")
async def delete_weight(val: float, db: AsyncSession = Depends(get_db)):
    cfg = await _get_or_create_config(db)
    data = dict(cfg.data)
    weights = [w for w in data.get("weights", []) if abs(float(w.get("val", 0)) - val) > 0.01]
    data["weights"] = weights
    cfg.data = data
    cfg.version += 1
    db.add(cfg)
    await db.commit()
    return {"ok": True, "weights": data["weights"], "version": cfg.version}

# HUB OPERATIONS
@router.post("/hub")
async def add_hub(payload: HubAddRequest, db: AsyncSession = Depends(get_db)):
    cfg = await _get_or_create_config(db)
    data = dict(cfg.data)
    hubs = list(data.get("hubs", []))
    hubs = [h for h in hubs if h.get("code") != payload.code]
    hubs.append(payload.model_dump())
    data["hubs"] = hubs
    cfg.data = data
    cfg.version += 1
    db.add(cfg)
    await db.commit()
    return {"ok": True, "hubs": data["hubs"], "version": cfg.version}

@router.delete("/hub/{code}")
async def delete_hub(code: str, db: AsyncSession = Depends(get_db)):
    cfg = await _get_or_create_config(db)
    data = dict(cfg.data)
    hubs = [h for h in data.get("hubs", []) if h.get("code") != code]
    data["hubs"] = hubs
    cfg.data = data
    cfg.version += 1
    db.add(cfg)
    await db.commit()
    return {"ok": True, "hubs": data["hubs"], "version": cfg.version}

# BROADCAST / NOTICE OPERATIONS
@router.post("/broadcast")
async def post_broadcast(payload: BroadcastRequest, db: AsyncSession = Depends(get_db)):
    cfg = await _get_or_create_config(db)
    data = dict(cfg.data)
    data["notice_banner"] = {
        "title": payload.title,
        "message": payload.message,
        "severity": payload.severity,
        "active": True
    }
    cfg.data = data
    cfg.version += 1
    db.add(cfg)
    await db.commit()
    return {"ok": True, "notice_banner": data["notice_banner"], "version": cfg.version}

@router.delete("/broadcast")
async def clear_broadcast(db: AsyncSession = Depends(get_db)):
    cfg = await _get_or_create_config(db)
    data = dict(cfg.data)
    data["notice_banner"] = None
    cfg.data = data
    cfg.version += 1
    db.add(cfg)
    await db.commit()
    return {"ok": True, "notice_banner": None, "version": cfg.version}

# ALLOWANCE
@router.post("/allowance")
async def set_default_allowance(amount: int, db: AsyncSession = Depends(get_db)):
    cfg = await _get_or_create_config(db)
    data = dict(cfg.data)
    data["driver_allowance_default"] = amount
    cfg.data = data
    cfg.version += 1
    db.add(cfg)
    await db.commit()
    return {"ok": True, "driver_allowance_default": amount, "version": cfg.version}
