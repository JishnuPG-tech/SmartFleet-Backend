import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from app.core.database import AsyncSessionLocal, init_db
from app.core.security import get_password_hash
from app.models import (
    User,
    Driver,
    Truck,
    Trip,
    ProofOfDelivery,
    OperationalAlert,
    TelemetryLog,
)

async def seed_data():
    print("🚀 Initializing database schema...")
    await init_db()
    
    async with AsyncSessionLocal() as session:
        # Check if already seeded
        res = await session.execute(select(User).limit(1))
        if res.scalars().first():
            print("ℹ️ Database already contains data. Skipping initial seeding.")
            return

        print("🌱 Seeding SmartFleet database with Kerala operational fleet...")

        # 1. Admin User
        admin_user = User(
            id=str(uuid.uuid4()),
            phone="+91 98950 00000",
            full_name="Fleet Manager (Kochi HQ)",
            role="admin",
            hashed_password=get_password_hash("1234"),
            avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200",
            is_active=True,
        )
        session.add(admin_user)

        # 2. Drivers & Users
        drivers_data = [
            {
                "phone": "+91 94471 23456",
                "name": "Suresh Kumar",
                "license": "KL-07-2015-008912",
                "exp": 12,
                "truck": "KL 11 AB 1234",
                "status": "on_trip",
                "trips": 142
            },
            {
                "phone": "+91 98460 78901",
                "name": "Rajesh Varma",
                "license": "KL-11-2018-004521",
                "exp": 8,
                "truck": "KL 07 CD 5678",
                "status": "available",
                "trips": 98
            },
            {
                "phone": "+91 97455 11223",
                "name": "Biju Pavithran",
                "license": "KL-01-2012-009943",
                "exp": 15,
                "truck": "KL 09 EF 9012",
                "status": "available",
                "trips": 215
            },
        ]

        driver_objs = []
        for d in drivers_data:
            u = User(
                id=str(uuid.uuid4()),
                phone=d["phone"],
                full_name=d["name"],
                role="driver",
                hashed_password=get_password_hash("1234"),
                is_active=True
            )
            session.add(u)
            await session.flush()

            dp = Driver(
                id=u.id,
                license_number=d["license"],
                experience_years=d["exp"],
                current_truck_plate=d["truck"],
                status=d["status"],
                total_trips_completed=d["trips"]
            )
            session.add(dp)
            driver_objs.append(dp)

        # 3. Kerala Commercial Trucks
        now = datetime.now(timezone.utc)
        trucks_data = [
            {
                "plate": "KL 11 AB 1234",
                "model": "BharatBenz 2823R",
                "capacity": 28.0,
                "status": "on_trip",
                "driver_id": driver_objs[0].id,
                "lat": 10.5276,
                "lng": 76.2144,
                "heading": 348.0,
                "speed": 42.5
            },
            {
                "plate": "KL 07 CD 5678",
                "model": "Tata Prima 3530.K",
                "capacity": 35.0,
                "status": "available",
                "driver_id": driver_objs[1].id,
                "lat": 9.9312,
                "lng": 76.2673,
                "heading": 0.0,
                "speed": 0.0
            },
            {
                "plate": "KL 09 EF 9012",
                "model": "Ashok Leyland 4220",
                "capacity": 42.0,
                "status": "available",
                "driver_id": driver_objs[2].id,
                "lat": 10.7867,
                "lng": 76.6548,
                "heading": 0.0,
                "speed": 0.0
            },
            {
                "plate": "KL 14 GH 3456",
                "model": "Eicher Pro 6028",
                "capacity": 28.0,
                "status": "in_workshop",
                "driver_id": None,
                "lat": 11.2588,
                "lng": 75.7804,
                "heading": 0.0,
                "speed": 0.0
            }
        ]

        for t in trucks_data:
            tr = Truck(
                plate=t["plate"],
                model=t["model"],
                capacity_tons=t["capacity"],
                status=t["status"],
                assigned_driver_id=t["driver_id"],
                last_latitude=t["lat"],
                last_longitude=t["lng"],
                last_heading=t["heading"],
                last_speed_kmh=t["speed"],
                last_telemetry_at=now
            )
            session.add(tr)

        # 4. Trips
        # Running Trip TR-1025
        trip_running = Trip(
            id="TR-1025",
            origin_city="Kochi Port",
            origin_code="COK",
            origin_lat=9.9312,
            origin_lng=76.2673,
            dest_city="Kozhikode Hub",
            dest_code="CCJ",
            dest_lat=11.2588,
            dest_lng=75.7804,
            cargo_title="24.5T Industrial Steel",
            weight_tons=24.5,
            truck_plate="KL 11 AB 1234",
            driver_id=driver_objs[0].id,
            status="running",
            scheduled_start=now - timedelta(hours=3),
            actual_started_at=now - timedelta(hours=2, minutes=45),
            total_distance_km=180.0,
            distance_done_km=76.5,
            allowance_amount=1500,
            is_paid=False
        )
        session.add(trip_running)

        # Waiting Trip TR-1026
        trip_waiting = Trip(
            id="TR-1026",
            origin_city="Ernakulam Goods Yard",
            origin_code="ERS",
            origin_lat=9.9816,
            origin_lng=76.2999,
            dest_city="Thiruvananthapuram Central",
            dest_code="TRV",
            dest_lat=8.5241,
            dest_lng=76.9366,
            cargo_title="32T Cement Bags",
            weight_tons=32.0,
            truck_plate="KL 07 CD 5678",
            driver_id=driver_objs[1].id,
            status="waiting",
            scheduled_start=now + timedelta(hours=5),
            total_distance_km=215.0,
            distance_done_km=0.0,
            allowance_amount=1500,
            is_paid=False
        )
        session.add(trip_waiting)

        # Delivered Trip TR-1024 with POD
        trip_delivered = Trip(
            id="TR-1024",
            origin_city="Kannur Depot",
            origin_code="CAN",
            origin_lat=11.8745,
            origin_lng=75.3704,
            dest_city="Kozhikode Port",
            dest_code="CCJ",
            dest_lat=11.2588,
            dest_lng=75.7804,
            cargo_title="18T Ceramic Tiles",
            weight_tons=18.0,
            truck_plate="KL 09 EF 9012",
            driver_id=driver_objs[2].id,
            status="delivered",
            scheduled_start=now - timedelta(days=1, hours=6),
            actual_started_at=now - timedelta(days=1, hours=5),
            delivered_at=now - timedelta(days=1, hours=1),
            total_distance_km=90.0,
            distance_done_km=90.0,
            allowance_amount=1200,
            is_paid=True,
            paid_at=now - timedelta(hours=18)
        )
        session.add(trip_delivered)
        await session.flush()

        pod = ProofOfDelivery(
            trip_id="TR-1024",
            otp_code="5824",
            otp_verified_at=now - timedelta(days=1, hours=1),
            photo_url="/uploads/pod/sample_cargo_pod.jpg",
            signature_svg="<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 100'><path d='M20 50 Q 80 10 140 60 T 180 40' fill='none' stroke='#000' stroke-width='2'/></svg>",
            recipient_name="K. Ramanathan (Warehouse Supervisor)",
            recipient_notes="All 18T ceramic tiles verified undamaged."
        )
        session.add(pod)

        # 5. Operational Alerts
        alerts_data = [
            {
                "plate": "KL 14 GH 3456",
                "trip_id": None,
                "severity": "urgent",
                "title": "Brake System Air Pressure Low",
                "description": "Vehicle in Kozhikode workshop pending master cylinder replacement."
            },
            {
                "plate": "KL 11 AB 1234",
                "trip_id": "TR-1025",
                "severity": "warning",
                "title": "NH-66 Heavy Traffic Near Edappally",
                "description": "Speed dropped to 18 km/h. Estimated ETA delayed by +25 mins."
            }
        ]

        for a in alerts_data:
            al = OperationalAlert(
                truck_plate=a["plate"],
                trip_id=a["trip_id"],
                severity=a["severity"],
                title=a["title"],
                description=a["description"],
                is_resolved=False
            )
            session.add(al)

        # 6. Sample Telemetry Breadcrumbs for Running Trip TR-1025
        waypoints = [
            (9.9657, 76.2711, 40.0, 340.0),
            (10.0125, 76.2990, 52.0, 345.0),
            (10.1500, 76.3200, 58.0, 350.0),
            (10.3500, 76.2500, 60.0, 348.0),
            (10.4800, 76.2200, 55.0, 345.0),
            (10.5276, 76.2144, 42.5, 348.0),
        ]
        for i, (lat, lng, spd, hdg) in enumerate(waypoints):
            t = TelemetryLog(
                truck_plate="KL 11 AB 1234",
                trip_id="TR-1025",
                latitude=lat,
                longitude=lng,
                heading=hdg,
                speed_kmh=spd,
                battery_level=95 - i,
                recorded_at=now - timedelta(minutes=(len(waypoints) - i) * 10)
            )
            session.add(t)

        await session.commit()
        print("✅ Successfully seeded SmartFleet database with Kerala operational fleet!")

if __name__ == "__main__":
    asyncio.run(seed_data())
