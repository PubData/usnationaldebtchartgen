function(chart) {
    var ren = this.renderer;

    ren.label('As-Of:<br>National Debt:', 100, 55)
        .attr({
            fill: 'rgba(0, 0, 0)',
            padding: 8,
            zIndex: 6
        })
        .css({
            fontSize: '14px',
            lineHeight: '20px',
            fontWeight: 'bold',
            color: 'white',
        })
        .add()
        .shadow(true)
}
