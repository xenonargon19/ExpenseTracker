from datetime import date
from db import (
    get_conn,
    achievement_exists,
    insert_achievement,
)

ACHIEVEMENTS = [
    {
        "key": "save_5000",
        "title": "Saved 5,000",
        "description": "You have saved a total of 5,000.",
    },
    {
        "key": "save_10000",
        "title": "Saved 10,000",
        "description": "You have saved a total of 10,000.",
    },
    {
        "key": "first_purchase",
        "title": "First Purchase",
        "description": "You bought your first target.",
    },
]



def check_and_unlock_achievements():
    """
    Checks achievement conditions against current DB state.
    Inserts newly unlocked achievements.
    Returns list of newly unlocked achievement keys.
    """
    unlocked = []
    today = date.today().isoformat()

    conn = get_conn()
    cur = conn.cursor()

    # ---- total_saved achievements ----
    cur.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions")
    total_saved = max(0, cur.fetchone()[0])

    if total_saved >= 5000 and not achievement_exists("save_5000"):
        insert_achievement("save_5000", today)
        unlocked.append("save_5000")

    if total_saved >= 10000 and not achievement_exists("save_10000"):
        insert_achievement("save_10000", today)
        unlocked.append("save_10000")

    # ---- purchase achievement ----
    cur.execute("SELECT COUNT(*) FROM purchases")
    purchase_count = cur.fetchone()[0]

    if purchase_count >= 1 and not achievement_exists("first_purchase"):
        insert_achievement("first_purchase", today)
        unlocked.append("first_purchase")

    conn.close()
    return unlocked
