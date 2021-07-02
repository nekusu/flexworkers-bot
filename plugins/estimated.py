from traceback import print_exc
from configparser import ConfigParser
from pyrogram import Client, filters
import flexpoolapi
from data import get_earnings

config = ConfigParser()
config.read('config.ini')
miner = flexpoolapi.miner(config['bot']['eth_address'])


@Client.on_message(filters.chat(int(config['bot']['chat_id'])) & filters.command(['estimated', 'estimate']))
def estimated(client, message):
	print(message.text)
	wait_message = client.send_message(message.chat.id, "Wait a second...")
	days = 7

	try:
		if len(message.command) > 1:
			days = int(message.command[1])

		estimated_eth = miner.estimated_daily_revenue() / pow(10, 18)
		total_eth = estimated_eth * days
		reply = "**Estimated for {} day{}**{}".format(days, 's' if days > 1 else '', get_earnings(total_eth))
	except Exception as e:
		print_exc()
		reply = "An error ocurred:\n`{}`".format(e)

	client.edit_message_text(message.chat.id, wait_message.message_id, reply)
