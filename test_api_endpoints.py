import httpx
import json

base_url = "http://127.0.0.1:8000"

with httpx.Client(base_url=base_url, timeout=10.0) as client:
    # 1. Health
    r = client.get("/health")
    print("1. /health ->", r.status_code, r.json())
    assert r.status_code == 200

    # 2. Docs
    r = client.get("/docs")
    print("2. /docs ->", r.status_code, "HTML length:", len(r.text))
    assert r.status_code == 200

    # 3. Auth Login
    r = client.post("/api/v1/auth/login", json={"phone": "+91 98950 00000", "password": "1234"})
    print("3. /api/v1/auth/login ->", r.status_code, r.json())
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 4. Auth Me
    r = client.get("/api/v1/auth/me", headers=headers)
    print("4. /api/v1/auth/me ->", r.status_code, r.json())
    assert r.status_code == 200

    # 5. Trucks
    r = client.get("/api/v1/trucks")
    trucks = r.json()
    plates = [x.get("plate") for x in trucks]
    print(f"5. /api/v1/trucks -> {r.status_code}, Loaded {len(trucks)} trucks: {plates}")
    assert r.status_code == 200 and len(trucks) >= 4

    # 6. Drivers
    r = client.get("/api/v1/drivers")
    drivers = r.json()
    names = [x.get("full_name") for x in drivers]
    print(f"6. /api/v1/drivers -> {r.status_code}, Loaded {len(drivers)} drivers: {names}")
    assert r.status_code == 200 and len(drivers) >= 3

    # 7. Trips
    r = client.get("/api/v1/trips")
    trips = r.json()
    trip_ids = [x.get("id") for x in trips]
    print(f"7. /api/v1/trips -> {r.status_code}, Loaded {len(trips)} trips: {trip_ids}")
    assert r.status_code == 200 and len(trips) >= 3

    # 8. Telemetry Ping
    ping_payload = {
        "truck_plate": "KL 11 AB 1234",
        "trip_id": "TR-1025",
        "latitude": 10.6012,
        "longitude": 76.1855,
        "heading": 350.5,
        "speed_kmh": 46.2,
        "battery_level": 94
    }
    r = client.post("/api/v1/telemetry/ping", json=ping_payload)
    print("8. /api/v1/telemetry/ping ->", r.status_code, r.json())
    assert r.status_code == 200

    # 9. POD OTP Verification (both otp and otp_code)
    r = client.post("/api/v1/pod/TR-1025/verify-otp", json={"otp": "5824"})
    print("9a. /api/v1/pod/TR-1025/verify-otp (otp) ->", r.status_code, r.json())
    assert r.status_code == 200

    r = client.post("/api/v1/pod/TR-1025/verify-otp", json={"otp_code": "5824"})
    print("9b. /api/v1/pod/TR-1025/verify-otp (otp_code) ->", r.status_code, r.json())
    assert r.status_code == 200

    # 10. OTA App CMS Config
    r = client.get("/api/v1/config/app")
    print("10. /api/v1/config/app ->", r.status_code, "Version:", r.json()["version"])
    assert r.status_code == 200 and "emergency_contacts" in r.json()

    # 11. Earnings Summary
    r = client.get("/api/v1/earnings/driver/summary", headers=headers)
    print("11. /api/v1/earnings/driver/summary ->", r.status_code, r.json()["driver_name"], "Pending:", r.json()["pending_payout_amount"])
    assert r.status_code == 200

    # 12. Alerts
    r = client.get("/api/v1/alerts")
    alerts = r.json()
    titles = [x.get("title") for x in alerts]
    print(f"12. /api/v1/alerts -> {r.status_code}, Found {len(alerts)} alerts: {titles}")
    assert r.status_code == 200

print("\nALL FASTAPI ENDPOINT CHECKS PASSED WITH 100% SUCCESS!")
