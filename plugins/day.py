from shared import config, get_earnings, get_summary
from traceback import print_exc
import os
from json import load
from datetime import datetime, timedelta
from pyrogram import Client, filters
import flexpoolapi


@Client.on_message(filters.chat(int(config()['bot']['chat_id'])) & filters.command('day'))
def day(client, message):
	print(message.text)
	cfg = config()['bot']
	miner = flexpoolapi.miner('ETH', cfg['eth_address'])
	wait_message = client.send_message(message.chat.id, 'Wait a second...')
	date = datetime.today()

	try:
		if len(message.command) > 1:
			if message.command[1] == 'yesterday':
				date = (datetime.today() - timedelta(1)).strftime('%Y-%m-%d')
			else:
				date = datetime.strptime(message.command[1], '%Y-%m-%d').strftime('%Y-%m-%d')

			if os.path.isfile(f'earnings/{date}.json'):
				with open(f'earnings/{date}.json', 'r') as earnings_file:
					earnings = load(earnings_file)

				reply = get_summary(earnings, date)
			else:
				reply = f'No data saved on {date}.'
		else:
			if os.path.exists('earnings/_last_day.json'):
				with open('earnings/_last_day.json', 'r') as last_day_file:
					last_day = load(last_day_file)

				total_balance = (miner.payments_stats().stats.total_paid + miner.balance().balance) / pow(10, 18)
				total_eth = total_balance - last_day['total_balance']
				reply = f"Address: `{cfg['eth_address']}`\n\n**Today's earnings**{get_earnings(total_eth)}"
			else:
				reply = f"No data stored for address `{cfg['eth_address']}`."
	except Exception as e:
		print_exc()
		reply = f'An error ocurred:\n`{e}`'

	client.edit_message_text(message.chat.id, wait_message.message_id, reply)
