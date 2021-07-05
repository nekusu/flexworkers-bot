from apscheduler.schedulers.background import BackgroundScheduler
from pyrogram import Client
from earnings import daily_earnings

app = Client('flex_workbot')
scheduler = BackgroundScheduler()
scheduler.add_job(daily_earnings, 'cron', hour='13', minute='10', args=[app])
scheduler.start()
app.run()
