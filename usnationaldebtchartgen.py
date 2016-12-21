from urllib import request
import cgi
import io
import json
from datetime import datetime, timedelta
from flask import Flask, request as flask_request, send_file, abort
from lxml import html
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

	end_date = scrape_effective_date()
	start_date = (end_date - timedelta(days=365))

	# Prepare the post_data
	h = {'Content-Type':'application/json', 'User-Agent': 'curl'}
	post_data = {}
	post_data['options'] = \
		'{}data: [\n{}\n{}'.format(
			options.split('data: [\n')[0],
			render_to_options(scrape_history_data(start_date, end_date)),
			options.split('data: [\n')[1])

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

def scrape_effective_date():
	# Scrape the "current" (effective) date from the U.S. Treasury site.
	url = 'https://treasurydirect.gov/NP/debt/current'

	req = request.Request(url=url)

	with request.urlopen(req) as response:
		page = response.read()

	tree = html.fromstring(page)
	date_str = tree.xpath('//table[@class="data1"]/tr/td[1]/text()')[0]
	return datetime.strptime(date_str, '%m/%d/%Y')


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


def render_to_options(history_data):
	# Produce a string containing the history data ready for insert into the
	# options string that gets passed to the Highcharts export server.
	output = ''

	for row in history_data:
		# Add row of data as:
		# [Date.UTC(yyyy, mm, dd), amount],
		date_str = 'Date.UTC({}, {}, {})'.format(
			row['date'].year, row['date'].month - 1, row['date'].day)

		output += '[{}, {:.2f}],\n'.format(date_str, row['amount'])

	output = '{}'.format(output[:-2])  # On the last line, no comma.

	if output:
		# Add newline on last line.
		output += '\n'

	return output
