from configparser import ConfigParser
from pyrogram import Client, filters

config = ConfigParser()
config.read('config.ini')


@Client.on_message(filters.chat(config['bot']['user']) & filters.command('help'))
def help(client, message):
	print(message.text)
	reply = "**Available Commands**\
		\n\n/day __yesterday__ | __YYYY-mm-dd__ - Get earnings.\
		\n/summary __start__ | __end__ - Get summary.\
		\n/price __currency__ - Get current ETH price.\
		\n/estimated __days__ - Get estimated earnings.\
		\n/currency __symbol__ - Change your currency.\
		\n/workers - List workers."
	client.send_message(message.chat.id, reply)
