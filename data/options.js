{
        credits: {
            text: 'DebtToThePenny.com',
            href: 'https://www.DebtToThePenny.com'
        },
        title: {
            text: 'U.S. Public National Debt'
        },
        subtitle: {
            text: ''
        },
        legend: {
            enabled: false
        },
        exporting: {
            buttons: {
                contextButton: {
                    enabled: false
                }
            }
        },
        xAxis: {
            type: 'datetime',
            ordinal: false
        },
        yAxis: [{
            title: {
                text: 'Debt Amount (Trillions)',
                style: {
                    color: Highcharts.getOptions().colors[0]
                }
            },
            labels: {
                formatter: function () {
                    return '$' + (this.value / Math.pow(10, 12)).toFixed(1) + 'T';
                },
                style: {
                    color: Highcharts.getOptions().colors[0]
                }
            }
        }],
        series: [{
            name: 'National Debt',
            type: 'area',
            data: [
            ],
            threshold: null,
            fillColor: {
                linearGradient: {
                    x1: 0,
                    y1: 0,
                    x2: 0,
                    y2: 1
                },
                stops: [
                    [0, Highcharts.getOptions().colors[0]],
                    [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                ]
            }
        }]
}
