from configparser import ConfigParser
from datetime import datetime
from cryptocompare import get_price
import flexpoolapi

def config():
	config = ConfigParser()
	config.read('config.ini')
	return config

def save_config(option, value):
	config = ConfigParser()
	config.read('config.ini')
	config['bot'][option] = value

	with open('config.ini', 'w') as config_file:
		config.write(config_file)

def revenue(earnings, price, worker='Total'):
	return f"\n`{earnings:.6f}` ETH ~ `{earnings * price:>7.2f}` {config()['bot']['currency']} > {worker}"

def share(name, percentage):
	return f'{name} (`{percentage:.1f}`%)'

def get_earnings(total_eth):
	cfg = config()['bot']
	miner = flexpoolapi.miner('ETH', cfg['eth_address'])
	eth_price = get_price('ETH', currency=cfg['currency'])['ETH'][cfg['currency']]
	total_valid_shares = miner.stats().valid_shares
	reply = ''

	for worker in miner.workers():
		shares_percentage = worker.valid_shares / total_valid_shares * 100
		earnings = shares_percentage / 100 * total_eth
		reply += revenue(earnings, eth_price, share(worker.name, shares_percentage))

	return reply + revenue(total_eth, eth_price)

def get_summary(earnings, start_date='', end_date=''):
	cfg = config()['bot']
	eth_price = get_price('ETH', currency=cfg['currency'])['ETH'][cfg['currency']]
	start_date = datetime.strptime(start_date, '%Y-%m-%d')
	reply = f"Address: `{cfg['eth_address']}`\n"
	reply += f"\n**{start_date.strftime('%d %B %Y')}**"

	if end_date:
		end_date = datetime.strptime(end_date, '%Y-%m-%d')
		reply += f"** - {end_date.strftime('%d %B %Y')}**"
		days_difference = (end_date - start_date).days + 1

	for worker in earnings['workers']:
		earnings_percentage = earnings['workers'][worker] / earnings['total'] * 100
		reply += revenue(earnings['workers'][worker], eth_price, share(worker, earnings_percentage))

	reply += revenue(earnings['total'], eth_price)

	if days_difference > 1:
		average_earnings = { 'workers': {}, 'total': earnings['total'] / days_difference }
		reply += '\n\n**Average per Day**'

		for worker in earnings['workers']:
			average_earnings['workers'][worker] = earnings['workers'][worker] / days_difference
			reply += revenue(average_earnings['workers'][worker], eth_price, worker)

		reply += revenue(average_earnings['total'], eth_price)

	return reply
