from traceback import print_exc
import os
from json import load
from configparser import ConfigParser
from datetime import datetime, timedelta
from pyrogram import Client, filters
import flexpoolapi
from data import get_earnings, get_summary

config = ConfigParser()
config.read('config.ini')
miner = flexpoolapi.miner(config['bot']['eth_address'])


@Client.on_message(filters.chat(int(config['bot']['chat_id'])) & filters.command('day'))
def day(client, message):
	config.read('config.ini')
	print(message.text)
	wait_message = client.send_message(message.chat.id, "Wait a second...")
	date = datetime.today()

	try:
		if len(message.command) > 1:
			if message.command[1] == 'yesterday':
				date = (datetime.today() - timedelta(1)).strftime('%Y-%m-%d')
			else:
				date = datetime.strptime(message.command[1], '%Y-%m-%d').strftime('%Y-%m-%d')

			if os.path.isfile('earnings/{}.json'.format(date)):
				with open('earnings/{}.json'.format(date), 'r') as earnings_file:
					earnings = load(earnings_file)

				reply = get_summary(earnings, date)
			else:
				reply = "No data saved on {}.".format(date)
		else:
			if os.path.exists('earnings/_last_day.json'):
				with open('earnings/_last_day.json', 'r') as last_day_file:
					last_day = load(last_day_file)

				total_balance = (miner.total_paid() + miner.balance()) / pow(10, 18)
				total_eth = total_balance - last_day['total_balance']
				reply = "**Today's earnings**{}".format(get_earnings(total_eth))
			else:
				reply = "No data stored for address `{}`.".format(config['bot']['eth_address'])
	except Exception as e:
		print_exc()
		reply = "An error ocurred:\n`{}`".format(e)

	client.edit_message_text(message.chat.id, wait_message.message_id, reply)
