import enum


class SystemRole(str, enum.Enum):
    ADMIN = "ADMIN"
    HEALTH_WORKER = "HEALTH_WORKER"
    ANALYST = "ANALYST"
    VIEWER = "VIEWER"


class SystemPermission(str, enum.Enum):
    RECORDS_READ = "records:read"
    RECORDS_WRITE = "records:write"
    RECORDS_DELETE = "records:delete"
    OBSERVATIONS_READ = "observations:read"
    OBSERVATIONS_WRITE = "observations:write"
    ALERTS_READ = "alerts:read"
    ALERTS_MANAGE = "alerts:manage"
    SYNC_PUSH = "sync:push"
    SYNC_PULL = "sync:pull"
    ANALYTICS_READ = "analytics:read"
    USERS_MANAGE = "users:manage"
    ROLES_MANAGE = "roles:manage"


ROLE_PERMISSIONS_MAP: dict[SystemRole, list[SystemPermission]] = {
    SystemRole.ADMIN: list(SystemPermission),
    SystemRole.HEALTH_WORKER: [
        SystemPermission.RECORDS_READ,
        SystemPermission.RECORDS_WRITE,
        SystemPermission.OBSERVATIONS_READ,
        SystemPermission.OBSERVATIONS_WRITE,
        SystemPermission.ALERTS_READ,
        SystemPermission.SYNC_PUSH,
        SystemPermission.SYNC_PULL,
    ],
    SystemRole.ANALYST: [
        SystemPermission.RECORDS_READ,
        SystemPermission.OBSERVATIONS_READ,
        SystemPermission.ALERTS_READ,
        SystemPermission.ANALYTICS_READ,
    ],
    SystemRole.VIEWER: [
        SystemPermission.RECORDS_READ,
        SystemPermission.OBSERVATIONS_READ,
        SystemPermission.ALERTS_READ,
    ],
}
