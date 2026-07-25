import os


def _parse_admin_values(raw_value: str | None) -> set[str | int]:
    if not raw_value:
        return set()

    values: set[str | int] = set()
    for item in raw_value.split(","):
        value = item.strip()
        if not value:
            continue

        try:
            values.add(int(value))
        except ValueError:
            values.add(value)

    return values


ADMIN_ID = int(os.getenv("ADMIN_ID", "6593118456"))
ADMIN_IDS = _parse_admin_values(os.getenv("ADMIN_IDS"))


def is_admin_user(user_id: int, username: str | None = None) -> bool:
    if user_id == ADMIN_ID:
        return True

    if user_id in ADMIN_IDS:
        return True

    if username is None:
        return False

    normalized_username = username.lstrip("@").lower()
    normalized_admins = {
        str(value).lstrip("@").lower() if isinstance(value, str) else str(value)
        for value in ADMIN_IDS
    }
    return normalized_username in normalized_admins
