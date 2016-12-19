# usnationaldebtchartgen
U.S. National Debt - Chart Generator

## Synopsis
Generate chart image, pdf, or SVG of the U.S. National Public Debt from data scraped from the U.S. Treasury website.

The output for the chart is generated by the open source [Highcharts export server](https://export.highcharts.com).

The chart is best viewed in a browser thanks to another project: [PubData.github.io/usnationaldebtchart](https://pubdata.github.io/usnationaldebtchart/)

## Installation
This is a Flask app (Python3).

``` sh
$ cd [your workspace]
$ git clone https://github.com/pubdata/usnationaldebtchartgen.git
$ cd usnationaldebtchartgen
$ virtualenv -p python3 venv
$ source venv/bin/activate
$ pip install -r requirements.txt
``` 

Further deploy instructions will vary based on production system requirements.

For testing, use gunicorn:

``` sh
$ gunicorn usnationaldebtchartgen:app
``` 

From a browser, access the app using: [http://localhost:8000/chart](http://localhost:8000/chart)

Optionally, you can specify the filename and file extension (.png, .jpg, .pdf, or .svg) to access a specific output format.  For images and PDFs, you can also specify the image width (e.g., bob-1200.jpg for a 1200 pixel wide JPEG image with a personalized filename).

## Example

- [DebtToThePenny.com/chart](https://www.debttothepenny.com/chart) (Default, serves chart.png, 600x400.)
- [DebtToThePenny.com/chart/chart-800.png](https://www.debttothepenny.com/chart/chart-800.png) (Serves 800 pixel wide image.)
- [DebtToThePenny.com/chart/chart.jpg](https://www.debttothepenny.com/chart/chart.jpg) (Serves a JPEG image.)
- [DebtToThePenny.com/chart/chart.pdf](https://www.debttothepenny.com/chart/chart.pdf) (Serves a PDF document.)
- [DebtToThePenny.com/chart/chart.svg](https://www.debttothepenny.com/chart/chart.svg) (Serves an SVG+XML.)
- [DebtToThePenny.com/chart/Bob.jpg](https://www.debttothepenny.com/chart/Bob.jpg) (Serves a JPEG image with the personalized filename Bob.jpg.)


## License

MIT
