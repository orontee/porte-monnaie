var months = $("a.month-anchor");
var amounts = $("td.amount");
var averages = $("td.average");
var i, data = [], amount, average;
var cleanUp = function (str) {
    return str.replace(',', '.').replace('&nbsp;', '');
};
for (i = 0; i < months.length; i++) {
    amount = Number(cleanUp(amounts[i].innerHTML));
    average = ((averages[i] !== undefined)
               ? Number(cleanUp(averages[i].innerHTML))
               : undefined);
    if (!isNaN(amount)) {
        data.push({'amount': amount,
                   'average': average,
                   'month': months[i].innerHTML});
    }
}

var margin = {top: 30, right: 40, bottom: 60, left: 40},
    width = 600 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;

var x = d3.scale.ordinal().rangeRoundBands([0, width], 0.1);

var y0 = d3.scale.linear().range([height, 0]);

var xAxis = d3.svg.axis().scale(x).orient("bottom");

var yAxisLeft = d3.svg.axis().scale(y0).ticks(6).orient("left");

var svg = d3.select("#graph-body").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var names = [gettext("Your expenditures"), gettext("Average")];

var legendData = d3.values(names);

x.domain(data.map(function(d) { return d.month; }));
y0.domain([0, d3.max(data, function(d) {
    if (d.average !== undefined) {
        return Math.max(d.amount, d.average);
    }
    return d.amount;
})]);

svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis)
    .selectAll("text")
    .style("text-anchor", "end")
    .attr("dx", "-.8em")
    .attr("dy", ".15em")
    .attr("transform", function(d) {
        return "rotate(-65)";
    });

svg.append("g")
    .attr("class", "y axis axisLeft")
    .call(yAxisLeft)
    .append("text")
    .attr("y", 6)
    .attr("dy", "-2em")
    .style("text-anchor", "end")
    .style("text-anchor", "end")
    .text("€");

bars = svg.selectAll(".bar").data(data).enter();

bars.append("rect")
    .attr("class", "bar0")
    .attr("x", function(d) { return x(d.month); })
    .attr("width", x.rangeBand()/2)
    .attr("y", function(d) { return y0(d.amount); })
    .attr("height", function(d,i,j) { return height - y0(d.amount); });

bars.append("rect")
    .attr("class", "bar1")
    .attr("x", function(d) { return x(d.month) + x.rangeBand()/2; })
    .attr("width", x.rangeBand() / 2)
    .attr("y", function(d) { return y0(d.average); })
    .attr("height", function(d,i,j) { return height - y0(d.average); });

legend = svg.selectAll(".legend")
    .data(legendData.slice())
    .enter()
    .append("g")
    .attr("class", "legend")
    .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

legend.append("rect")
    .attr("x", width - 18)
    .attr("width", 18)
    .attr("height", 18)
    .attr("class", function(d, i) { return "bar" + i; });

legend.append("text")
    .attr("x", width - 24)
    .attr("y", 9)
    .attr("dy", ".35em")
    .style("text-anchor", "end")
    .text(function(d) { return d; });

