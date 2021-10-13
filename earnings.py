from shared import config, get_summary
from traceback import print_exc
import os
from datetime import datetime, timedelta
from json import load, dump
from pyrogram import Client
import flexpoolapi


def daily_earnings(app):
	cfg = config()['bot']
	miner = flexpoolapi.miner('ETH', cfg['eth_address'])
	total_balance = (miner.payments_stats().stats.total_paid + miner.balance().balance) / pow(10, 18)
	last_day = { 'address': cfg['eth_address'], 'total_balance': total_balance, 'earnings': 0.0 }

	if not os.path.exists('earnings'):
		os.mkdir('earnings')

	if os.path.exists('earnings/_last_day.json'):
		with open('earnings/_last_day.json', 'r') as last_day_file:
			last_day = load(last_day_file)

		today_earnings = total_balance - last_day['total_balance']
		last_day['total_balance'] = total_balance
		last_day['earnings'] = today_earnings
		total_valid_shares = miner.stats().valid_shares
		earnings = { 'workers': {}, 'total': today_earnings, 'total_balance': total_balance }

		for worker in miner.workers():
			earnings['workers'][worker.name] = worker.valid_shares / total_valid_shares * today_earnings

		date = (datetime.today() - timedelta(1)).strftime('%Y-%m-%d')

		with open(f'earnings/{date}.json', 'w') as earnings_file:
			dump(earnings, earnings_file, indent=4)

		try:
			text = get_summary(earnings, date)
			print(f'{date}: Workers earnings saved successfully!')
			app.send_message(int(cfg['chat_id']), text)
		except Exception:
			print(f'{date}: An error occurred when the bot tried to send a message to the chat, earnings are saved successfully.')
			print_exc()

	with open('earnings/_last_day.json', 'w') as last_day_file:
		dump(last_day, last_day_file, indent=4)

if __name__ == '__main__':
	app = Client('flex_workbot')

	with app:
		daily_earnings(app)
