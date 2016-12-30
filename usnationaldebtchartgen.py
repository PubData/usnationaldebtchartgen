import cgi
import io
import json
import pathlib
from datetime import datetime, timedelta
from urllib import request
from lxml import html
from flask import Flask, request as flask_request, send_file, abort
import jinja2
from werkzeug.utils import secure_filename


app = Flask(__name__)


@app.route('/chart/', methods=['GET'])
@app.route('/chart/<filename>-<width_str>.<file_ext>', methods=['GET'])
@app.route('/chart/<filename>.<file_ext>', methods=['GET'])
@app.route('/chart/<filename>', methods=['GET'])
def chart(filename='chart', file_ext='png', width_str=None):
	url="http://export.highcharts.com"
	output_types = {
		'png': 'image/png',
		'jpg': 'image/jpeg',
		'jpeg': 'image/jpeg',
		'pdf': 'application/pdf',
		'svg': 'image/svg+xml',
		'svg+xml': 'image/svg+xml',
		'xml': 'image/svg+xml',
	}

	if file_ext and file_ext.lower() not in output_types:
		abort(404)

	# Read options.js from filesystem into a variable.
	with app.open_resource('data/options.js', 'r') as f:
		options = f.read()

	# Read callback.js from filesystem into a variable.
	if pathlib.Path('data/callback.js').is_file():
		with app.open_resource('data/callback.js', 'r') as f:
			callback = f.read()

	current = scrape_current()

	start_date = (current['date'] - timedelta(days=365))
	history_data = scrape_history_data(start_date, current['date'])

	# Prepare the post_data
	h = {'Content-Type':'application/json', 'User-Agent': 'curl'}
	post_data = {}
	post_data['options'] = \
		jinja2.Template(options).render({
			'date': current.get('date'),
			'amount': current.get('amount'),
			'history_data': history_data})

	if 'callback' in locals():
		post_data['callback'] = callback;

	if file_ext and file_ext != 'png':
		post_data['type'] = output_types.get(file_ext.lower(), 'image/png')
	if (post_data.get('type') == 'image/svg+xml' and \
			flask_request.args.get('scale')):
		post_data['scale'] = flask_request.args.get('scale')
	if width_str and int(width_str) > 0:
		post_data['width'] = int(width_str)

	post_data_json = json.dumps(post_data).encode('utf-8')

	req = request.Request(url=url, data=post_data_json, headers=h)

	with request.urlopen(req) as response:
		mimetype = response.headers['Content-Type']
		image_data = io.BytesIO(response.read())

	return send_file(
		image_data,
		attachment_filename=secure_filename('{}.{}'.format(filename, file_ext)),
		mimetype=mimetype)


def scrape_current():
	# Scrape the "current" (effective) date from the U.S. Treasury site.
	url = 'https://treasurydirect.gov/NP/debt/current'

	req = request.Request(url=url)

	with request.urlopen(req) as response:
		page = response.read()

	tree = html.fromstring(page)
	date_str = tree.xpath('//table[@class="data1"]/tr/td[1]/text()')[0]
	amount_str = tree.xpath('//table[@class="data1"]/tr/td[4]/text()')[0]

	return {
		'date': datetime.strptime(date_str, '%m/%d/%Y'),
		'amount': float(amount_str.replace(',', ''))}


def scrape_history_data(start_date, end_date):
	# Scrape history data from the search results of the US Treasury site.
	url = (
		"https://treasurydirect.gov/NP/debt/search?" +
		"startMonth={}&startDay={}&startYear={}" +
		"&endMonth={}&endDay={}&endYear={}")

	url = url.format(
			start_date.month,
			start_date.day,
			start_date.year,
			end_date.month,
			end_date.day,
			end_date.year)

	req = request.Request(url=url)

	with request.urlopen(req) as response:
		page = response.read()

	tree = html.fromstring(page)
	history_data = []

	for row in tree.xpath('//table[@class="data1"]/tr[position()>1]'):
		date_str = row.xpath('./td')[0].xpath('text()')[0]
		date = datetime.strptime(date_str, '%m/%d/%Y')
		amount_str = row.xpath('./td')[3].xpath('text()')[0]
		amount = float(amount_str.replace(',', ''))

		history_data.append({'date': date, 'amount': amount})

	return history_data
