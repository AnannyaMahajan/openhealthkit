"""
OpenHealthKit Quickstart Example
Demonstrates initializing the toolkit database and executing simple record operations.
"""

import asyncio
from openhealthkit.database import init_db, AsyncSessionLocal
from openhealthkit.models import HealthRecord, Observation
from openhealthkit.alerts import alert_engine


async def run_quickstart():
    print("🚀 Initializing OpenHealthKit database...")
    await init_db()

    async with AsyncSessionLocal() as db:
        # Create a health record
        record = HealthRecord(
            patient_identifier="PATIENT-QS-001",
            age_years=34,
            gender="Female",
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        print(f"✅ Created HealthRecord ID: {record.id}")

        # Add observation with threshold
        obs = Observation(
            health_record_id=record.id,
            observation_type="fever_body_temp_c",
            value_number=39.2,
            unit="°C",
        )
        db.add(obs)
        await db.commit()
        await db.refresh(obs)
        print(f"✅ Logged Observation: {obs.observation_type} = {obs.value_number}{obs.unit}")

        # Trigger alert evaluation
        alerts = await alert_engine.evaluate_observation(db, obs)
        await db.commit()
        print(f"🔔 Alerts Triggered: {len(alerts)}")


if __name__ == "__main__":
    asyncio.run(run_quickstart())
