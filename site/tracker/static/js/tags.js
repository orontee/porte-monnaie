var fill = d3.scale.category20();

var margin = {top: 0, right: 20, bottom: 0, left: 20},
    width = 600 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;

function draw(words) {
    d3.select("#tags-body").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")")
        .selectAll("text")
        .data(words)
        .enter().append("text")
        .style("font-size", function(d) { return 10 + 2 * d.count + "px"; })
        .style("font-family", "Impact")
        .style("fill", function(d, i) { return fill(i); })
        .attr("text-anchor", "middle")
        .attr("transform", function(d) {
            return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
        })
        .text(function(d) { return d.name; })
        .on("click", function(d) {
            window.location = "/tracker/expenditures/search/?filter=" + d.name;
        });
}

function buildTagCloud(url) {
    $.ajax({
        url: url,
        cache: false
    }).done(function(words) {
        d3.layout.cloud().size([width + margin.left + margin.right,
                                height + margin.top + margin.bottom])
            .words(words)
            .rotate(function() { return ~~(Math.random() * 2) * 90; })
            .font("Impact")
            .fontSize(function(d) {
                return 10 + 2 * d.count;
            })
            .on("end", draw)
            .start();
    });
}
