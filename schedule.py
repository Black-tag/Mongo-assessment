import asyncio
from caching import get_client
from datetime import datetime, date, time
from zoneinfo import ZoneInfo
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os
from dotenv import load_dotenv


load_dotenv()


SCHEDULE_HOUR = 15
SCHEDULE_MINUTE = 22


async def init_scheduler():
    # Schedule email for the specified time
    ist = ZoneInfo("Asia/Kolkata")
    now = datetime.now(ist)
    run_at = now.replace(
        hour=SCHEDULE_HOUR, minute=SCHEDULE_MINUTE, second=0, microsecond=0
    )
    asyncio.create_task(worker_loop())
    await schedule_email("rudra.pratap@digicollect.com", run_at)
    print("password loaded:", os.getenv("APP_PASSWORD"))
    print(f"Email scheduled for {run_at} (timestamp: {run_at.timestamp()})")
    print(f"Current time: {datetime.now()} (timestamp: {datetime.now().timestamp()})")


conf = ConnectionConfig(
    MAIL_USERNAME="anand.a@digicollect.com",
    MAIL_PASSWORD=os.getenv("APP_PASSWORD"),
    MAIL_FROM="anand.a@digicollect.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)




async def send_email(email):
    message = MessageSchema(
        subject="DCForms Daily Report",
        recipients=[email],
        body="<h2>hi, good afternoon</h2>",
        subtype="html",
    )
    fm = FastMail(conf)
    await fm.send_message(message)
    print(f"✓ Email sent to {email}")


async def worker_loop():

    while True:
        try:
            print("worker tick, checking jobs...")
            client = await get_client()
            current_time = datetime.now().timestamp()
            jobs = await client.zrangebyscore("email_queue", 0, current_time)
            print(f"due jobs: {jobs}")

        
            for job in jobs:
                await client.zrem("email_queue", job)  # ← remove first
                try:
                    await send_email(job)
                except Exception as e:
                    print(f"✗ Email failed for {job}: {e}")

            await asyncio.sleep(5)
        except Exception as e:
            print(f"✗ Worker error: {e}")
            await asyncio.sleep(5)


async def schedule_email(email: str, run_at: datetime):
    client = await get_client()
    timestamp = run_at.timestamp()
    await client.zadd("email_queue", {email: timestamp})
