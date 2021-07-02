from configparser import ConfigParser
from pyrogram import Client, filters
from cryptocompare import get_price

config = ConfigParser()
config.read('config.ini')


@Client.on_message(filters.chat(int(config['bot']['chat_id'])) & filters.command('price'))
def price(client, message):
	config.read('config.ini')
	print(message.text)
	wait_message = client.send_message(message.chat.id, "Wait a second...")
	currency = message.command[1].upper() if len(message.command) > 1 else config['bot']['currency']

	try:
		price = get_price('ETH', currency=config['bot']['currency'])['ETH'][config['bot']['currency']]
		reply = '**Ether (ETH) Price:** `{}` {}'.format(price, currency)
	except Exception:
		reply = '{} is not available.'.format(currency)

	client.edit_message_text(message.chat.id, wait_message.message_id, reply)
