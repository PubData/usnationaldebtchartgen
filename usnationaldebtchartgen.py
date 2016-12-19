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
    
    req = request.Request(url='https://treasurydirect.gov/NP/debt/current')

    with request.urlopen(req) as response:
        page = response.read()

    tree = html.fromstring(page)
    end_date_str = tree.xpath('//table[@class="data1"]/tr/td[1]/text()')[0]
    end_date = datetime.strptime(end_date_str, '%m/%d/%Y')
    start_date = (end_date - timedelta(days=365))

    req = request.Request(
        url="https://treasurydirect.gov/NP/debt/search?startMonth={}&startDay={}&startYear={}&endMonth={}&endDay={}&endYear={}".format(
            start_date.month,
            start_date.day,
            start_date.year,
            end_date.month,
            end_date.day,
            end_date.year))

    with request.urlopen(req) as response:
        page = response.read()

    tree = html.fromstring(page)
    records = ''

    for row in tree.xpath('//table[@class="data1"]/tr[position()>1]'):
        date_str = row.xpath('./td')[0].xpath('text()')[0]
        amount_str = row.xpath('./td')[3].xpath('text()')[0]
        date = datetime.strptime(date_str, '%m/%d/%Y')
        # Add row of data as:
        # [Date.UTC(yyyy, mm, dd), amount],
        records += (
            '[{}, {}],\n'.format(
                'Date.UTC({}, {}, {})'.format(date.year, date.month - 1, date.day),
                amount_str.replace(',', '')));

    records = '{}\n'.format(records[:-2])  # On the last line, no comma.

    with app.open_resource('data/infile.js', 'r') as f:
        infile = f.read()

    url="http://export.highcharts.com"
    h = {'Content-Type':'application/json', 'User-Agent': 'curl'}
    post_data = {}
    post_data['infile'] = \
        '{}data: [\n{}\n{}'.format(
            infile.split('data: [\n')[0],
            records,
            infile.split('data: [\n')[1])

    if file_ext and file_ext != 'png':
        post_data['type'] = output_types.get(file_ext.lower(), 'image/png')
    if (post_data.get('type') == 'image/svg+xml' and \
            flask_request.args.get('scale')):
        post_data['scale'] = flask_request.args.get('scale')
    if width_str and int(width_str) > 0:
        post_data['width'] = int(width_str)
        
    data = json.dumps(post_data).encode('utf-8')
    req = request.Request(url=url, data=data, headers=h)
    fd = request.urlopen(req)
    image_data = io.BytesIO(fd.read())

    return send_file(
        image_data,
        attachment_filename=secure_filename('{}.{}'.format(filename, file_ext)),
        mimetype=fd.headers['Content-Type'])
