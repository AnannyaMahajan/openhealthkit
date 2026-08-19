"""
OpenHealthKit Safe Seed Script
Generates synthetic, clearly labeled demo data for testing and local development.
No PII or real medical data is used.
"""

import asyncio
import json
import random
import uuid
from datetime import datetime, timedelta, timezone

from openhealthkit.alerts import alert_engine
from openhealthkit.auth import SystemRole
from openhealthkit.database import AsyncSessionLocal, init_db
from openhealthkit.models import (
    Alert,
    AlertRule,
    AlertSeverity,
    AlertStatus,
    Community,
    HealthRecord,
    Observation,
    Organization,
    Role,
    User,
)
from openhealthkit.utils.logger import logger
from openhealthkit.utils.security import hash_password
from sqlalchemy.future import select


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


SYNTHETIC_COMMUNITIES = [
    {"name": "Alpha Community - Sector 4", "location": "District North (Synthetic Zone)"},
    {"name": "Beta Village Health Outpost", "location": "District East (Synthetic Zone)"},
    {"name": "Gamma River Basin Settlement", "location": "District South (Synthetic Zone)"},
    {"name": "Delta Highland Camp", "location": "District West (Synthetic Zone)"},
]

OBSERVATION_TYPES = [
    {"type": "water_turbidity_ntu", "unit": "NTU", "min": 0.5, "max": 15.0, "thresh": 5.0},
    {"type": "fever_body_temp_c", "unit": "°C", "min": 36.5, "max": 40.2, "thresh": 38.5},
    {"type": "systolic_bp_mmHg", "unit": "mmHg", "min": 90.0, "max": 170.0, "thresh": 140.0},
    {"type": "diastolic_bp_mmHg", "unit": "mmHg", "min": 60.0, "max": 110.0, "thresh": 90.0},
    {"type": "blood_glucose_mg_dl", "unit": "mg/dL", "min": 70.0, "max": 250.0, "thresh": 180.0},
]


async def seed():
    logger.info("Initializing DB for seeding...")
    await init_db()

    async with AsyncSessionLocal() as db:
        # Check if already seeded
        comm_check = await db.execute(select(Community))
        if comm_check.scalars().first():
            logger.info("Database already contains seed data. Skipping.")
            return

        logger.info("Seeding Organizations & Communities...")
        org = Organization(
            name="Synthetic Global Health Initiative",
            code="SGHI-DEMO",
            description="Demo Organization for OpenHealthKit Testing",
        )
        db.add(org)
        await db.flush()

        communities = []
        for c_data in SYNTHETIC_COMMUNITIES:
            comm = Community(
                name=c_data["name"],
                location_name=c_data["location"],
                organization_id=org.id,
            )
            db.add(comm)
            communities.append(comm)
        await db.flush()

        logger.info("Seeding Alert Rules...")
        rules = [
            AlertRule(
                name="High Water Turbidity Warning",
                observation_type="water_turbidity_ntu",
                condition_operator=">",
                threshold_value=5.0,
                severity=AlertSeverity.HIGH.value,
                cooldown_minutes=30,
            ),
            AlertRule(
                name="High Fever Alert",
                observation_type="fever_body_temp_c",
                condition_operator=">",
                threshold_value=38.5,
                severity=AlertSeverity.CRITICAL.value,
                cooldown_minutes=15,
            ),
            AlertRule(
                name="Hypertension Stage 2 Threshold",
                observation_type="systolic_bp_mmHg",
                condition_operator=">=",
                threshold_value=140.0,
                severity=AlertSeverity.MEDIUM.value,
                cooldown_minutes=60,
            ),
        ]
        db.add_all(rules)
        await db.flush()

        logger.info("Seeding Synthetic Health Records & Observations...")
        for i in range(1, 26):
            comm = random.choice(communities)
            patient_code = f"SYNTH-PATIENT-{1000 + i}"
            hr = HealthRecord(
                patient_identifier=patient_code,
                age_years=random.randint(5, 75),
                gender=random.choice(["Male", "Female", "Other"]),
                community_id=comm.id,
                metadata_json=json.dumps({"demo": True, "seed_batch": "v0.1.0"}),
            )
            db.add(hr)
            await db.flush()

            # Add 2-3 observations per health record
            for _ in range(random.randint(2, 3)):
                obs_def = random.choice(OBSERVATION_TYPES)
                val = round(random.uniform(obs_def["min"], obs_def["max"]), 1)
                observed_time = utc_now() - timedelta(hours=random.randint(1, 72))

                obs = Observation(
                    health_record_id=hr.id,
                    observation_type=obs_def["type"],
                    value_number=val,
                    unit=obs_def["unit"],
                    observed_at=observed_time,
                )
                db.add(obs)
                await db.flush()

                # Evaluate against alert engine
                await alert_engine.evaluate_observation(db, obs)

        await db.commit()
        logger.info("Successfully seeded synthetic demo data into OpenHealthKit!")


if __name__ == "__main__":
    asyncio.run(seed())
