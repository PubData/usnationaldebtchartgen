{
        credits: {
            text: 'DebtToThePenny.com',
        },
        title: {
            text: 'U.S. National Public Debt'
        },
        subtitle: {
            text: '{{ date.strftime('%B %-d, %Y') }}'
        },
        labels: {
            items: [{
                html: '{{ "${:,.2f}".format(amount) }}'
            }]
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
        yAxis: {
            title: {
                text: 'Amount (Trillions)',
            },
            labels: {
                formatter: function () {
                    return '$' + (this.value / Math.pow(10, 12)).toFixed(1) + 'T';
                }
            }
        },
        series: [{
            name: 'Public Debt',
            type: 'area',
            data: [
                {% set comma = joiner(",") -%}
                {% for row in history_data -%}
                    {{ comma() }}[Date.UTC({{ row.date.year }}, {{ row.date.month - 1 }}, {{ row.date.day }}), {{ row.amount }}]
                {% endfor %}
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
        }],
        legend: {
            enabled: false
        }
}
