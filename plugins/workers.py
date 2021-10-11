from traceback import print_exc
from configparser import ConfigParser
from pyrogram import Client, filters
import flexpoolapi

config = ConfigParser()
config.read('config.ini')
miner = flexpoolapi.miner('ETH', config['bot']['eth_address'])


@Client.on_message(filters.chat(int(config['bot']['chat_id'])) & filters.command(['workers', 'worker']))
def workers(client, message):
	config.read('config.ini')
	print(message.text)
	wait_message = client.send_message(message.chat.id, "Wait a second...")

	try:
		total_hashrate = miner.stats().reported_hashrate / pow(1000, 2)
		reply = "**Workers**"

		for worker in reversed(miner.workers()):
			worker_name = config['bot']['zil_worker_name'] if worker.name in config['bot']['zil_address'] else worker.name
			hashrate = worker.reported_hashrate / pow(1000, 2)
			hashrate_percentage = hashrate / total_hashrate * 100
			reply += "\n{}: `{:.2f}` MH/s (`{:.1f}`%)".format(worker_name, hashrate, hashrate_percentage)
	except Exception as e:
		print_exc()
		reply = "An error ocurred:\n`{}`".format(e)

	client.edit_message_text(message.chat.id, wait_message.message_id, reply)
