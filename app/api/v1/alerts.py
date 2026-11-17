from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.alert import OperationalAlert
from app.schemas.alert import AlertCreate, AlertOut
from app.services.websocket_manager import manager

router = APIRouter(prefix="/alerts", tags=["Operational Alerts"])

@router.get("", response_model=List[AlertOut])
async def list_alerts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OperationalAlert).order_by(OperationalAlert.created_at.desc()))
    return result.scalars().all()

@router.post("", response_model=AlertOut)
async def create_alert(req: AlertCreate, db: AsyncSession = Depends(get_db)):
    alert = OperationalAlert(
        truck_plate=req.truck_plate.strip(),
        trip_id=req.trip_id,
        severity=req.severity.value if hasattr(req.severity, 'value') else req.severity,
        title=req.title.strip(),
        description=req.description.strip()
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)

    # Broadcast urgent alerts to live fleet map
    await manager.broadcast_fleet({
        "type": "alert_created",
        "severity": alert.severity,
        "truck_plate": alert.truck_plate,
        "title": alert.title
    })

    return alert

@router.patch("/{id}/resolve", response_model=AlertOut)
async def resolve_alert(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OperationalAlert).filter(OperationalAlert.id == id.strip()))
    alert = result.scalars().first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_resolved = True
    alert.resolved_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(alert)
    return alert
