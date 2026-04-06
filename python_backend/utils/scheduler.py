from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from database.db import SessionLocal
from models.capsule import Capsule
from models.user import User
from utils.email import send_unlock_email
import urllib.request
import os

scheduler = BackgroundScheduler()


def keep_alive():
    """Ping own health endpoint so Render free tier doesn't spin down."""
    url = os.getenv("RENDER_EXTERNAL_URL")
    if url:
        try:
            urllib.request.urlopen(f"{url}/api/health", timeout=10)
            print("💓 Keep-alive ping sent")
        except Exception as e:
            print(f"⚠️ Keep-alive ping failed: {e}")


def check_and_unlock_capsules():
    """
    Runs every minute.
    Finds capsules whose unlock_date has passed, marks them unlocked,
    and sends a one-time email notification to the owner.
    """
    db = SessionLocal()
    try:
        now = datetime.now()

        # Find capsules that are due but not yet unlocked or emailed
        due_capsules = (
            db.query(Capsule)
            .filter(
                Capsule.unlock_date <= now,
                Capsule.is_unlocked == False,
            )
            .all()
        )

        for capsule in due_capsules:
            # Mark as unlocked
            capsule.is_unlocked = True

            # Send email only once
            if not capsule.email_sent:
                user = db.query(User).filter(User.id == capsule.user_id).first()
                if user:
                    success = send_unlock_email(user.email, capsule.title)
                    if success:
                        capsule.email_sent = True

        if due_capsules:
            db.commit()
            print(f"🔓 Unlocked {len(due_capsules)} capsule(s) at {now.strftime('%H:%M:%S')}")

    except Exception as e:
        print(f"❌ Scheduler error: {e}")
        db.rollback()
    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler — called once on app startup."""
    scheduler.add_job(
        check_and_unlock_capsules,
        trigger="interval",
        minutes=1,
        id="unlock_capsules",
        replace_existing=True,
    )
    scheduler.add_job(
        keep_alive,
        trigger="interval",
        minutes=14,
        id="keep_alive",
        replace_existing=True,
    )
    scheduler.start()
    print("⏰ Capsule unlock scheduler started (runs every 1 minute)")


def stop_scheduler():
    """Stop the scheduler — called on app shutdown."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("⏰ Scheduler stopped")
