from datetime import datetime
from configparser import ConfigParser
from cryptocompare import get_price
import flexpoolapi

config = ConfigParser()
config.read('config.ini')
miner = flexpoolapi.miner('ETH', config['bot']['eth_address'])


def get_earnings(total_eth):
	config.read('config.ini')
	eth_price = get_price('ETH', currency=config['bot']['currency'])['ETH'][config['bot']['currency']]
	total_valid_shares = miner.stats().valid_shares
	reply = ''

	for worker in miner.workers():
		worker_name = config['bot']['zil_worker_name'] if worker.name in config['bot']['zil_address'] else worker.name
		shares_percentage = worker.valid_shares / total_valid_shares * 100
		earnings = shares_percentage / 100 * total_eth
		reply += "\n`{:.6f}` ETH ~ `{:>7.2f}` {} | {} (`{:.1f}`%)".format(earnings, earnings * eth_price, config['bot']['currency'], worker_name, shares_percentage)

	return reply + "\n`{:.6f}` ETH ~ `{:>7.2f}` {} | Total".format(total_eth, total_eth * eth_price, config['bot']['currency'])

def get_summary(earnings, start_date='', end_date=''):
	config.read('config.ini')
	eth_price = get_price('ETH', currency=config['bot']['currency'])['ETH'][config['bot']['currency']]
	reply = "**{}{}**".format(datetime.strptime(start_date, '%Y-%m-%d').strftime('%d %B %Y'), ' - {}'.format(datetime.strptime(end_date, '%Y-%m-%d').strftime('%d %B %Y')) if end_date else '')
	days_difference = (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days + 1 if end_date else 0

	for worker in earnings['workers']:
		earnings_percentage = earnings['workers'][worker] / earnings['total'] * 100
		reply += "\n`{:.6f}` ETH ~ `{:>7.2f}` {} | {} (`{:.1f}`%)".format(earnings['workers'][worker], earnings['workers'][worker] * eth_price, config['bot']['currency'],
			worker, earnings_percentage)

	reply += "\n`{:.6f}` ETH ~ `{:>7.2f}` {} | Total".format(earnings['total'], earnings['total'] * eth_price, config['bot']['currency'])

	if days_difference > 1:
		average_earnings = {'workers': {}, 'total': earnings['total'] / days_difference}
		reply += "\n\n**Average per Day**"

		for worker in earnings['workers']:
			average_earnings['workers'][worker] = earnings['workers'][worker] / days_difference
			reply += "\n`{:.6f}` ETH ~ `{:>7.2f}` {} | {}".format(average_earnings['workers'][worker], average_earnings['workers'][worker] * eth_price, config['bot']['currency'], worker)

		reply += "\n`{:.6f}` ETH ~ `{:>7.2f}` {} | Total".format(average_earnings['total'], average_earnings['total'] * eth_price, config['bot']['currency'])

	return reply
