import os, matplotlib
from json import load
from configparser import ConfigParser
from datetime import datetime, timedelta
from pyrogram import Client, filters
from matplotlib import pyplot as plt
import pandas as pd
import flexpoolapi
from data import get_summary

config = ConfigParser()
config.read('config.ini')
matplotlib.style.use('seaborn-dark')
miner = flexpoolapi.miner(config['bot']['eth_address'])


def generate_graph(data, type, title):
	start_month = data['days'][0].month
	end_month = data['days'][-1].month if data['days'][-1].month != start_month else None
	df = pd.DataFrame(data[type], index=[d.day for d in data['days']])
	plot = df.plot.bar(rot=0, figsize=(10, 6), stacked=True) if type == 'bars' else df.plot.line(figsize=(10, 6))
	plot.legend(loc='upper center', ncol=5, title='Workers')
	plt.title('{}{} | {}'.format(data['days'][0].strftime('%B'), ' - {}'.format(data['days'][-1].strftime('%B')) if end_month else '', title))
	plt.xlabel('Days')
	plt.ylabel('ETH')
	fig = plot.get_figure()
	fig.savefig('{}.png'.format(type))

def send_graphs(data, client, chat_id):
	generate_graph(data, 'bars', 'Earnings per Day')
	generate_graph(data, 'lines', 'Accumulated Earnings')
	client.send_photo(chat_id, 'bars.png')
	client.send_photo(chat_id, 'lines.png')

@Client.on_message(filters.chat(config['bot']['user']) & filters.command('summary'))
def summary(client, message):
	print(message.text)
	wait_message = client.send_message(message.chat.id, "Wait a second...")
	reply_message = None
	start_date = datetime.today().replace(day=1, month=datetime.today().month - 1 if datetime.today().day == 1 else datetime.today().month).strftime('%Y-%m-%d')
	end_date = (datetime.today() - timedelta(1)).strftime('%Y-%m-%d')

	if len(message.command) > 1:
		start_date = message.command[1]
	if len(message.command) > 2:
		end_date = message.command[2]

	date = start_date
	summary = {'workers': {}, 'total': 0.0}
	plot_data = {'bars': {}, 'lines': {'Total': []}, 'days': []}

	while date <= end_date:
		if os.path.isfile('earnings/{}.json'.format(date)):
			with open('earnings/{}.json'.format(date), 'r') as earnings_file:
				earnings = load(earnings_file)

			for worker in earnings['workers']:
				if not worker in summary['workers']:
					summary['workers'][worker] = earnings['workers'][worker]
					plot_data['bars'][worker] = []
					plot_data['lines'][worker] = []
				else:
					summary['workers'][worker] += earnings['workers'][worker]

				plot_data['bars'][worker].append(earnings['workers'][worker])
				plot_data['lines'][worker].append(summary['workers'][worker])

			plot_data['days'].append(datetime.strptime(date, '%Y-%m-%d'))
			summary['total'] += earnings['total']
			plot_data['lines']['Total'].append(summary['total'])
		else:
			if summary['total'] != 0.0:
				send_graphs(plot_data, client, message.chat.id)
				reply = get_summary(summary, start_date, date)
				reply_message = client.edit_message_text(message.chat.id, wait_message.message_id, reply)

			client.send_message(message.chat.id, "No data saved on {}.".format(date))
			start_date = (datetime.strptime(date, '%Y-%m-%d') + timedelta(1)).strftime('%Y-%m-%d')
			plot_data = {'bars': {}, 'lines': {'Total': []}, 'days': []}

		date = (datetime.strptime(date, '%Y-%m-%d') + timedelta(1)).strftime('%Y-%m-%d')

	send_graphs(plot_data, client, message.chat.id)
	reply = get_summary(summary, start_date, end_date)

	if reply_message:
		client.send_message(message.chat.id, reply)
	else:
		client.edit_message_text(message.chat.id, wait_message.message_id, reply)
