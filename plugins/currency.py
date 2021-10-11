from shared import config, save_config
from pyrogram import Client, filters
from cryptocompare import get_price


@Client.on_message(filters.chat(int(config()['bot']['chat_id'])) & filters.command('currency'))
def currency(client, message):
	print(message.text)
	cfg = config()['bot']
	wait_message = client.send_message(message.chat.id, 'Wait a second...')
	currency = message.command[1].upper() if len(message.command) > 1 else ''

	if currency:
		try:
			get_price('ETH', currency=currency)['ETH']
			save_config('currency', currency)
			reply = f'Symbol changed to {currency} successfully.'
		except Exception as e:
			print(e)
			reply = f'{currency} is not available.'
	else:
		reply = f"Current symbol: {cfg['currency']}."

	client.edit_message_text(message.chat.id, wait_message.message_id, reply, disable_web_page_preview=True)
