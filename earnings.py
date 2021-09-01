from traceback import print_exc
import os
from datetime import datetime, timedelta
from json import load, dump
from configparser import ConfigParser
from pyrogram import Client
import flexpoolapi
from data import get_summary

config = ConfigParser()


def daily_earnings(app):
	config.read('config.ini')
	miner = flexpoolapi.miner('ETH', config['bot']['eth_address'])
	total_balance = (miner.payments_stats().stats.total_paid + miner.balance().balance) / pow(10, 18)
	last_day = { 'address': config['bot']['eth_address'], 'total_balance': total_balance, 'earnings': 0.0 }

	if not os.path.exists('earnings'):
		os.mkdir('earnings')

	if os.path.exists('earnings/_last_day.json'):
		with open('earnings/_last_day.json', 'r') as last_day_file:
			last_day = load(last_day_file)

		today_earnings = total_balance - last_day['total_balance']
		last_day['total_balance'] = total_balance
		last_day['earnings'] = today_earnings
		total_valid_shares = miner.stats().valid_shares
		earnings = { 'workers': {}, 'total': today_earnings }

		for worker in miner.workers():
			earnings['workers'][config['bot']['zil_worker_name'] if worker.name in config['bot']['zil_address'] else worker.name] = miner.stats(worker.name).valid_shares / total_valid_shares * today_earnings

		date = (datetime.today() - timedelta(1)).strftime('%Y-%m-%d')

		with open('earnings/{}.json'.format(date), 'w') as earnings_file:
			dump(earnings, earnings_file, indent=4)

		try:
			text = get_summary(earnings, date)
			print("{}: Workers earnings saved successfully!".format(date))
			app.send_message(int(config['bot']['chat_id']), text)
		except Exception:
			print('{}: An error occurred when the bot tried to send a message to the chat, earnings are saved successfully.'.format(date))
			print_exc()

	with open('earnings/_last_day.json', 'w') as last_day_file:
		dump(last_day, last_day_file, indent=4)

if __name__ == "__main__":
	app = Client('flex_workbot')

	with app:
		daily_earnings(app)
