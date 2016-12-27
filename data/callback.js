function(chart) {
    var ren = this.renderer;

    ren.label(chart.options.labels.items[0].html, 80, 59)
        .css({
            fontSize: '40px',
            fontWeight: 'bold',
            color: 'black',
        })
        .add();
}
