from shared import config, share
from traceback import print_exc
from pyrogram import Client, filters
import flexpoolapi
from flexpoolapi.utils import format_hashrate


@Client.on_message(filters.chat(int(config()['bot']['chat_id'])) & filters.command(['workers', 'worker']))
def workers(client, message):
	print(message.text)
	cfg = config()['bot']
	miner = flexpoolapi.miner('ETH', cfg['eth_address'])
	wait_message = client.send_message(message.chat.id, "Wait a second...")

	try:
		stats = miner.stats()
		total_hashrate = format_hashrate(stats.average_effective_hashrate, 'eth')
		total_shares = stats.valid_shares
		reply = f"Address: `{cfg['eth_address']}`\n\n**Workers** __(last 24h)__"

		for worker in miner.workers():
			hashrate = format_hashrate(worker.average_effective_hashrate, 'eth')
			hashrate_percentage = worker.average_effective_hashrate / stats.average_effective_hashrate * 100
			reply += f'\n`{hashrate:>10}` ~ `{worker.valid_shares:>5}` shares > {share(worker.name, hashrate_percentage)}'

		reply += f'\n`{total_hashrate:>10}` ~ `{total_shares:>5}` shares > Total'
	except Exception as e:
		print_exc()
		reply = f'An error ocurred:\n`{e}`'

	client.edit_message_text(message.chat.id, wait_message.message_id, reply)
