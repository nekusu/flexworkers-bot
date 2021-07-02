import os
from datetime import datetime, timedelta
from json import load, dump
from configparser import ConfigParser
from apscheduler.schedulers.background import BackgroundScheduler
from pyrogram import Client
import flexpoolapi
from data import get_summary

app = Client('flex_workbot')
scheduler = BackgroundScheduler()
config = ConfigParser()


def daily_earnings():
	config.read('config.ini')
	miner = flexpoolapi.miner(config['bot']['eth_address'])
	total_balance = (miner.total_paid() + miner.balance()) / pow(10, 18)
	last_day = {'address': config['bot']['eth_address'], 'total_balance': total_balance, 'earnings': 0.0}

	if not os.path.exists('earnings'):
		os.mkdir('earnings')

	if os.path.exists('earnings/_last_day.json'):
		with open('earnings/_last_day.json', 'r') as last_day_file:
			last_day = load(last_day_file)

		today_earnings = total_balance - last_day['total_balance']
		last_day['total_balance'] = total_balance
		last_day['earnings'] = today_earnings
		total_valid_shares = miner.stats().valid_shares
		earnings = {'workers': {}, 'total': today_earnings}

		for worker in miner.workers():
			earnings['workers'][config['bot']['zil_worker_name'] if worker.worker_name in config['bot']['zil_address'] else worker.worker_name] = worker.stats().valid_shares / total_valid_shares * today_earnings

		date = (datetime.today() - timedelta(1)).strftime('%Y-%m-%d')

		with open('earnings/{}.json'.format(date), 'w') as earnings_file:
			dump(earnings, earnings_file, indent=4)

		text = get_summary(earnings, date)
		app.send_message(int(config['bot']['chat_id']), text)
		print("{}: Workers earnings saved successfully!".format(date))

	with open('earnings/_last_day.json', 'w') as last_day_file:
		dump(last_day, last_day_file, indent=4)

scheduler.add_job(daily_earnings, 'cron', hour='0', minute='5')
scheduler.start()
app.run()
