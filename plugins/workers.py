from traceback import print_exc
from configparser import ConfigParser
from pyrogram import Client, filters
import flexpoolapi

config = ConfigParser()
config.read('config.ini')
miner = flexpoolapi.miner(config['bot']['eth_address'])


@Client.on_message(filters.chat(int(config['bot']['chat_id'])) & filters.command(['workers', 'worker']))
def workers(client, message):
	config.read('config.ini')
	print(message.text)
	wait_message = client.send_message(message.chat.id, "Wait a second...")

	try:
		effective, reported = miner.current_hashrate()
		total_hashrate = reported / pow(1000, 2)
		reply = "**Workers**"

		for worker in reversed(miner.workers()):
			worker_name = config['bot']['zil_worker_name'] if worker.worker_name in config['bot']['zil_address'] else worker.worker_name
			effective, reported = worker.current_hashrate()
			hashrate = reported / pow(1000, 2)
			hashrate_percentage = hashrate / total_hashrate * 100
			reply += "\n{}: `{:.2f}` MH/s (`{:.1f}`%)".format(worker_name, hashrate, hashrate_percentage)
	except Exception as e:
		print_exc()
		reply = "An error ocurred with /estimated command:\n`{}`".format(e)

	client.edit_message_text(message.chat.id, wait_message.message_id, reply)
