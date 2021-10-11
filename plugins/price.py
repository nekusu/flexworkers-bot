from shared import config
from pyrogram import Client, filters
from cryptocompare import get_price


@Client.on_message(filters.chat(int(config()['bot']['chat_id'])) & filters.command('price'))
def price(client, message):
	cfg = config()['bot']
	print(message.text)
	wait_message = client.send_message(message.chat.id, 'Wait a second...')
	currency = message.command[1].upper() if len(message.command) > 1 else cfg['currency']

	try:
		price = get_price('ETH', currency=cfg['currency'])['ETH'][cfg['currency']]
		reply = f'**Ether (ETH) Price:** `{price}` {currency}'
	except Exception:
		reply = f'{currency} is not available.'

	client.edit_message_text(message.chat.id, wait_message.message_id, reply)
