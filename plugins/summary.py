from traceback import print_exc
import os, matplotlib
from json import load
from configparser import ConfigParser
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pyrogram import Client, filters
from matplotlib import pyplot as plt
import pandas as pd
import flexpoolapi
from data import get_summary

config = ConfigParser()
config.read('config.ini')
matplotlib.style.use('seaborn-dark')
miner = flexpoolapi.miner(config['bot']['eth_address'])


def get_all_workers(date, end_date):
	workers = []

	while date <= end_date:
		if os.path.isfile('earnings/{}.json'.format(date)):
			with open('earnings/{}.json'.format(date), 'r') as earnings_file:
				earnings = load(earnings_file)

			for worker in earnings['workers']:
				if not worker in workers:
					workers.append(worker)

		date = (datetime.strptime(date, '%Y-%m-%d') + timedelta(1)).strftime('%Y-%m-%d')

	return workers

def initialize_plot_data(total_workers):
	plot_data = { 'bars': {}, 'lines': {}, 'days': [] }

	for worker in total_workers:
		plot_data['bars'][worker] = []
		plot_data['lines'][worker] = []

	plot_data['lines']['Total'] = []
	return plot_data

def add_workers_earnings(summary, plot_data, earnings):
	for worker in summary['workers']:
		if worker in earnings['workers']:
			summary['workers'][worker] += earnings['workers'][worker]
			plot_data['bars'][worker].append(earnings['workers'][worker])
			plot_data['lines'][worker].append(plot_data['lines'][worker][-1] + earnings['workers'][worker] if len(plot_data['lines'][worker]) > 0 else 0)
		else:
			plot_data['bars'][worker].append(0)
			plot_data['lines'][worker].append(plot_data['lines'][worker][-1] if len(plot_data['lines'][worker]) > 0 else 0)

	summary['total'] += earnings['total']
	plot_data['lines']['Total'].append(plot_data['lines']['Total'][-1] + earnings['total'] if len(plot_data['lines']['Total']) > 0 else 0)

def generate_graph(data, type, title):
	df = pd.DataFrame(data[type], index=[d.day for d in data['days']])
	plot = df.plot.bar(rot=0, figsize=(10, 6), stacked=True) if type == 'bars' else df.plot.line(figsize=(10, 6))
	plot.legend(loc='upper center', ncol=5, title='Workers')
	plt.title('{} | {}'.format(data['days'][0].strftime('%B'), title))
	plt.xlabel('Days')
	plt.ylabel('ETH')
	fig = plot.get_figure()
	fig.savefig('{}.png'.format(type))

def send_graphs(data, client, chat_id):
	generate_graph(data, 'bars', 'Earnings per Day')
	generate_graph(data, 'lines', 'Accumulated Earnings')
	client.send_photo(chat_id, 'bars.png')
	client.send_photo(chat_id, 'lines.png')

@Client.on_message(filters.chat(int(config['bot']['chat_id'])) & filters.command('summary'))
def summary(client, message):
	print(message.text)
	wait_message = client.send_message(message.chat.id, "Wait a second...")
	start_date = datetime.today().replace(day=1, month=datetime.today().month + (-1 if datetime.today().day == 1 else 0)).strftime('%Y-%m-%d')
	end_date = (datetime.today() - timedelta(1)).strftime('%Y-%m-%d')

	try:
		if len(message.command) > 1:
			start_date = message.command[1]
		if len(message.command) > 2 and message.command[2] < end_date:
			end_date = message.command[2]

		date = start_date
		summary = { 'workers': {}, 'total': 0.0 }
		total_workers = get_all_workers(date, end_date)
		plot_data = initialize_plot_data(total_workers)

		for worker in total_workers:
			summary['workers'][worker] = 0

		while date <= end_date:
			end_month = (datetime.strptime(date, '%Y-%m-%d') + relativedelta(day=31)).strftime('%Y-%m-%d')
			earnings = None

			if os.path.isfile('earnings/{}.json'.format(date)):
				with open('earnings/{}.json'.format(date), 'r') as earnings_file:
					earnings = load(earnings_file)

			if earnings:
				add_workers_earnings(summary, plot_data, earnings)
			else:
				client.send_message(message.chat.id, "No data saved on {}.".format(date))
				plot_data['lines']['Total'].append(plot_data['lines']['Total'][-1] if len(plot_data['lines']['Total']) > 0 else 0)

			plot_data['days'].append(datetime.strptime(date, '%Y-%m-%d'))

			if date == end_month:
				send_graphs(plot_data, client, message.chat.id)
				plot_data = initialize_plot_data(total_workers)

			date = (datetime.strptime(date, '%Y-%m-%d') + timedelta(1)).strftime('%Y-%m-%d')

		if plot_data != initialize_plot_data(total_workers):
			send_graphs(plot_data, client, message.chat.id)

		reply = get_summary(summary, start_date, end_date)
	except Exception as e:
		print_exc()
		reply = "An error ocurred:\n`{}`".format(e)

	client.edit_message_text(message.chat.id, wait_message.message_id, reply)
