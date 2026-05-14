import asyncio
# from caching import get_client
from datetime import datetime, date, time
from zoneinfo import ZoneInfo
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
import os
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()


SCHEDULE_HOUR = 16
SCHEDULE_MINUTE = 00


async def init_scheduler():

    # ist = ZoneInfo("Asia/Kolkata")
    # now = datetime.now(ist)
    # run_at = now.replace(
    #     hour=SCHEDULE_HOUR, minute=SCHEDULE_MINUTE, second=0, microsecond=0
    # )
    # asyncio.create_task(worker_loop())
    recipient = "unnianandunni007@gmail.com"
    await send_email(recipient)
    # await schedule_email("unnianandunni007@gmail.com", run_at)
    # print(f"Email scheduled for {run_at} (timestamp: {run_at.timestamp()})")
    # print(f"Current time: {datetime.now()} (timestamp: {datetime.now().timestamp()})")


conf = ConnectionConfig(
    MAIL_USERNAME="anand.a@digicollect.com",
    MAIL_PASSWORD=os.getenv("APP_PASSWORD"),
    MAIL_FROM="anand.a@digicollect.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(email):
    message = MessageSchema(
        subject="UPDATE ON THE TASK: REDIS ASSIGNMENT",
        recipients=[email],
        template_body= {
            "username": "Anand",
            "verification_link": "https://localhost:3000"
        }, 
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    await fm.send_message(
        message,
        template_name = "welcome_email.html"
        )
    print(f"✓ Email sent to {email}")


# async def worker_loop():

#     while True:
#         try:
#             print("worker tick, checking jobs...")
#             client = await get_client()
#             current_time = datetime.now().timestamp()
#             jobs = await client.zrangebyscore("email_queue", 0, current_time)
#             print(f"due jobs: {jobs}")


#             for job in jobs:
#                 await client.zrem("email_queue", job)
#                 try:
#                     await send_email(job)
#                 except Exception as e:
#                     print(f"✗ Email failed for {job}: {e}")

#             await asyncio.sleep(5)
#         except Exception as e:
#             print(f"✗ Worker error: {e}")
#             await asyncio.sleep(5)


# async def schedule_email(email: str, run_at: datetime):
#     client = await get_client()
#     timestamp = run_at.timestamp()
#     await client.zadd("email_queue", {email: timestamp})


