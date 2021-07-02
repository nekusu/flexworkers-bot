from configparser import ConfigParser
from pyrogram import Client, filters
from cryptocompare import get_price

config = ConfigParser()
config.read('config.ini')


@Client.on_message(filters.chat(int(config['bot']['chat_id'])) & filters.command('currency'))
def currency(client, message):
	config.read('config.ini')
	print(message.text)
	wait_message = client.send_message(message.chat.id, "Wait a second...")
	currency = message.command[1].upper() if len(message.command) > 1 else ''

	if currency:
		try:
			get_price('ETH', currency=currency)['ETH']
			config['bot']['currency'] = currency

			with open('config.ini', 'w') as config_file:
				config.write(config_file)

			reply = "Symbol changed to {} successfully.".format(currency)
		except Exception as e:
			print(e)
			reply = "{} is not available.".format(currency)
	else:
		reply = "Current symbol: {}.".format(config['bot']['currency'])

	client.edit_message_text(message.chat.id, wait_message.message_id, reply, disable_web_page_preview=True)
