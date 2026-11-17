# SmartFleet 2.0 — Production Backend & Telematics Hub

High-performance, asynchronous fleet management and real-time telematics backend for Kerala logistics freight operations. Built with **FastAPI**, **SQLAlchemy 2.0 (asyncio)**, **PostgreSQL/PostGIS**, and **WebSockets**.

---

## Features
- **Real-Time GPS Telemetry Streaming**: WebSockets with client-side interpolation at  and .
- **Immutable Trip State Machine**:  ->  ->  ->  -> .
- **Timing-Safe Proof of Delivery (POD)**: 4-digit handover OTP validation using  with multipart photo upload and vector SVG signature archiving.
- **Daily Bata Allowance Settlements**: Automated tracking of commercial driver daily allowances with settlement ledger.
- **Dual-Engine Persistence**: Instant development on asynchronous SQLite (), seamless scale to PostgreSQL/PostGIS in production.
- **Auto-Generating OpenAPI 3.1 Specs**: Interactive documentation at  and .

---

## API Summary
| Group | Method | Endpoint | Description |
|---|---|---|---|
| **Auth** | POST |  | Fleet Owner/Admin login |
| **Auth** | POST |  | Driver SMS OTP request |
| **Auth** | POST |  | Driver OTP authentication |
| **Fleet** | GET |  | Live truck fleet with GPS coords |
| **Fleet** | GET |  | Commercial driver roster |
| **Trips** | GET |  | Query trips with status filters |
| **Trips** | POST |  | Create and dispatch new freight trip |
| **POD** | POST |  | Verify delivery handover OTP |
| **POD** | POST |  | Upload photo & signature, close trip |
| **Tele** | POST |  | Ingest driver GPS breadcrumb |
| **WS** | WS |  | Real-time fleet map coordinate stream |

---

## Quickstart


## Docker Deployment

