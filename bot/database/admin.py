import os

ADMIN_ID = int(os.getenv("ADMIN_ID", "6593118456"))
ADMIN_IDS = {
    int(item.strip())
    for item in os.getenv("ADMIN_IDS", "").split(",")
    if item.strip()
}


def is_admin_user(user_id: int) -> bool:
    return user_id in ADMIN_IDS or user_id == ADMIN_ID
