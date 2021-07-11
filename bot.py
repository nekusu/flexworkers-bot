from apscheduler.schedulers.background import BackgroundScheduler
from pyrogram import Client
from earnings import daily_earnings

app = Client('flex_workbot')
scheduler = BackgroundScheduler()
scheduler.add_job(daily_earnings, 'cron', hour='0', minute='5', args=[app], misfire_grace_time=180)
scheduler.start()
app.run()
