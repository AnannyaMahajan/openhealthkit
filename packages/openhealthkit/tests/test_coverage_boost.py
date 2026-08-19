import uuid
from datetime import datetime, timezone
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from openhealthkit.api.v1.alerts import create_alert_rule, list_alert_rules, list_alerts, update_alert_status
from openhealthkit.api.v1.analytics import get_analytics_summary
from openhealthkit.api.v1.auth import register_user, login_user, refresh_access_token, get_current_user_profile
from openhealthkit.api.v1.health import health_check, readiness_check
from openhealthkit.api.v1.observations import create_observation, list_observations
from openhealthkit.api.v1.records import create_health_record, get_health_record, list_health_records, update_health_record, delete_health_record
from openhealthkit.api.v1.sync import push_offline_changes, pull_remote_changes, resolve_sync_conflict
from openhealthkit.api.v1.users import create_user, list_roles, list_users
from openhealthkit.auth.jwt import create_access_token, create_refresh_token, decode_token
from openhealthkit.config import settings, DatabaseType
from openhealthkit.database import init_db
from openhealthkit.models.alert import Alert, AlertRule, AlertSeverity, AlertStatus
from openhealthkit.models.sync import SyncRecord, SyncState, SyncAction
from openhealthkit.models.user import User, Role
from openhealthkit.schemas.alert import AlertRuleCreate, AlertUpdateStatus
from openhealthkit.schemas.auth import UserRegister, UserLogin, RefreshTokenRequest
from openhealthkit.schemas.health_record import HealthRecordCreate, HealthRecordUpdate, ObservationCreate
from openhealthkit.schemas.sync import SyncPushRequest, SyncPushItem, SyncPullRequest, SyncConflictResolveRequest
from openhealthkit.schemas.user import UserCreate
from openhealthkit.utils.time import utc_now, format_iso, parse_iso
from openhealthkit.utils.security import hash_password, verify_password


@pytest.mark.asyncio
async def test_direct_api_coverage_boost(db_session: AsyncSession):
    # 1. Auth direct functions
    reg_req = UserRegister(
        username="directuser",
        email="direct@ohk.org",
        password="DirectPassword123!",
        full_name="Direct Test User",
    )
    user_read = await register_user(reg_req, db_session)
    assert user_read.username == "directuser"

    login_req = UserLogin(username_or_email="directuser", password="DirectPassword123!")
    token_res = await login_user(login_req, db_session)
    assert token_res.access_token is not None

    ref_res = await refresh_access_token(RefreshTokenRequest(refresh_token=token_res.refresh_token), db_session)
    assert ref_res.access_token is not None

    me_profile = await get_current_user_profile(user_read)
    assert me_profile.email == "direct@ohk.org"

    # 2. Health & Readiness
    h_res = await health_check()
    assert h_res["status"] == "healthy"

    # 3. Records direct functions
    rec_req = HealthRecordCreate(
        patient_identifier="SYNTH-PAT-DIRECT-001",
        age_years=42,
        gender="Male",
        observations=[
            ObservationCreate(
                observation_type="fever_body_temp_c",
                value_number=39.2,
                unit="°C",
            )
        ],
    )
    rec_read = await create_health_record(rec_req, db_session, current_user=user_read)
    assert rec_read.patient_identifier == "SYNTH-PAT-DIRECT-001"

    fetched_rec = await get_health_record(rec_read.id, db_session, current_user=user_read)
    assert fetched_rec.id == rec_read.id

    updated_rec = await update_health_record(
        rec_read.id,
        HealthRecordUpdate(age_years=43),
        db_session,
        current_user=user_read,
    )
    assert updated_rec.age_years == 43

    recs_list = await list_health_records(skip=0, limit=10, include_deleted=False, db=db_session, current_user=user_read)
    assert len(recs_list) >= 1

    # 4. Observations direct functions
    obs_req = ObservationCreate(
        health_record_id=rec_read.id,
        observation_type="systolic_bp_mmHg",
        value_number=145.0,
        unit="mmHg",
    )
    obs_read = await create_observation(obs_req, db_session, current_user=user_read)
    assert obs_read.observation_type == "systolic_bp_mmHg"

    obs_list = await list_observations(skip=0, limit=10, observation_type="systolic_bp_mmHg", db=db_session, current_user=user_read)
    assert len(obs_list) >= 1

    # 5. Alerts direct functions
    rule_req = AlertRuleCreate(
        name="High BP Rule",
        observation_type="systolic_bp_mmHg",
        condition_operator=">=",
        threshold_value=140.0,
        severity=AlertSeverity.HIGH,
        cooldown_minutes=15,
    )
    rule_read = await create_alert_rule(rule_req, db_session, current_user=user_read)
    assert rule_read.name == "High BP Rule"

    rules_list = await list_alert_rules(db_session, current_user=user_read)
    assert len(rules_list) >= 1

    alerts_list = await list_alerts(skip=0, limit=10, db=db_session, current_user=user_read)
    assert isinstance(alerts_list, list)

    if alerts_list:
        ack_alert = await update_alert_status(
            alerts_list[0].id,
            AlertUpdateStatus(status=AlertStatus.ACKNOWLEDGED),
            db_session,
            current_user=user_read,
        )
        assert ack_alert.status == "ACKNOWLEDGED"

    # 6. Users direct functions
    u_req = UserCreate(
        username="newuser_direct",
        email="newdirect@ohk.org",
        password="NewUserPass123!",
        full_name="New User Direct",
        role_names=["ANALYST"],
    )
    created_u = await create_user(u_req, db_session, current_user=user_read)
    assert created_u.username == "newuser_direct"

    users_list = await list_users(skip=0, limit=10, db=db_session, current_user=user_read)
    assert len(users_list) >= 1

    roles_list = await list_roles(db_session, current_user=user_read)
    assert len(roles_list) >= 1

    # 7. Analytics direct function
    analytics_summary = await get_analytics_summary(db_session, current_user=user_read)
    assert analytics_summary.total_health_records >= 1

    # 8. Sync direct functions
    push_req = SyncPushRequest(
        client_id="direct-device",
        items=[
            SyncPushItem(
                client_id="direct-device",
                entity_type="community",
                entity_id=str(uuid.uuid4()),
                action=SyncAction.CREATE,
                payload={"name": "Direct Community", "location_name": "District 1"},
                client_timestamp=datetime.now(timezone.utc),
            )
        ],
    )
    push_res = await push_offline_changes(push_req, db_session, current_user=user_read)
    assert push_res.processed_count == 1

    pull_res = await pull_remote_changes(
        SyncPullRequest(client_id="direct-device", since_timestamp=None),
        db_session,
        current_user=user_read,
    )
    assert isinstance(pull_res.items, list)

    # Delete record
    await delete_health_record(rec_read.id, db_session, current_user=user_read)


@pytest.mark.asyncio
async def test_settings_validation_and_init_db():
    # Test init_db execution
    await init_db()

    # Test settings validation in production mode
    prod_settings = settings.model_copy()
    prod_settings.ENV_MODE = "production"
    prod_settings.JWT_SECRET_KEY = "SECURE_PROD_SECRET_KEY_32CHARS_LONG_KEY!"
    prod_settings.INITIAL_ADMIN_PASSWORD = "ChangedAdminPass123!"
    validated = prod_settings.validate_production_settings()
    assert validated.ENV_MODE == "production"

    # Weak secret rejection test
    weak_settings = settings.model_copy()
    weak_settings.ENV_MODE = "production"
    weak_settings.JWT_SECRET_KEY = "DEV_SECRET_KEY"
    with pytest.raises(ValueError) as exc1:
        weak_settings.validate_production_settings()
    assert "CRITICAL SECURITY ERROR" in str(exc1.value)

    # Default admin password rejection test
    default_pass_settings = settings.model_copy()
    default_pass_settings.ENV_MODE = "production"
    default_pass_settings.JWT_SECRET_KEY = "SECURE_PROD_SECRET_KEY_32CHARS_LONG_KEY!"
    default_pass_settings.INITIAL_ADMIN_PASSWORD = "AdminPass123!ChangeMe"
    with pytest.raises(ValueError) as exc2:
        default_pass_settings.validate_production_settings()
    assert "INITIAL_ADMIN_PASSWORD" in str(exc2.value)
