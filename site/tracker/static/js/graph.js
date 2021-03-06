var months = $("tbody a.month-anchor");
var amounts = $("tbody td.amount");
var averages = $("tbody td.average");
var i, data = [], amount, average;
var hasAverages = false;
var histogramThreshold = 6;

function cleanUp(str) {
    return str.replace(',', '.').replace('&nbsp;', '');
}

function buildHistogram() {
    var legend, bars;
    var margin = {top: 30, right: 40, bottom: 60, left: 40},
        width = 550 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;

    var x = d3.scale.ordinal().rangeRoundBands([0, width], 0.1);

    var y0 = d3.scale.linear().range([height, 0]);

    var xAxis = d3.svg.axis().scale(x).orient("bottom");

    var yAxisLeft = d3.svg.axis().scale(y0).ticks(6).orient("left");

    var svg = d3.select("#histogram-container").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var rawLegendData = [{"class": "bar-amount",
                          "label": gettext("Your expenditures")}];
    if (hasAverages) {
        rawLegendData.push({"class": "bar-average",
                            "label": gettext("Average")});
    }
    var legendData = d3.values(rawLegendData);

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
        .attr("class", "bar-amount")
        .attr("x", function(d) { return x(d.month); })
        .attr("width", x.rangeBand() / (hasAverages ? 2 : 1))
        .attr("y", function(d) { return y0(d.amount); })
        .attr("height", function(d,i,j) { return height - y0(d.amount); });

    if (hasAverages) {
        bars.append("rect")
            .attr("class", "bar-average")
            .attr("x", function(d) { return x(d.month) + x.rangeBand()/2; })
            .attr("width", x.rangeBand() / 2)
            .attr("y", function(d) { return y0(d.average); })
            .attr("height", function(d,i,j) { return height - y0(d.average); });
    }
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
        .attr("class", function(d) { return d["class"]; });

    legend.append("text")
        .attr("x", width - 24)
        .attr("y", 9)
        .attr("dy", ".35em")
        .style("text-anchor", "end")
        .text(function(d) { return d.label; });

    document.getElementById('histogram-container').style.display = "inline";
}

for (i = 0; i < months.length; i++) {
    amount = Number(cleanUp(amounts[i].innerHTML));
    average = ((averages[i] !== undefined)
               ? Number(cleanUp(averages[i].innerHTML))
               : undefined);
    if (!isNaN(amount)) {
        data.push({'amount': amount,
                   'average': average,
                   'month': months[i].innerHTML});
        hasAverages |= (average !== undefined);
    }
}
if (months.length >= histogramThreshold) {
    buildHistogram();
}

var fill = d3.scale.category20(),
    tagsThreshold = 20;

var margin = {top: 0, right: 10, bottom: 0, left: 10},
    width = 550 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;

function buildTagCloud(baseUrl, year) {
    var wordsLimit = 100;
    var graph, countCloudBuilder, amountCloudBuilder,
        countExtent, amountExtent;
    
    function getUrl(ordering) {
        return baseUrl + '?limit=' +
            wordsLimit + '&ordering=' + ordering + '&year=' + year;
    }

    graph = d3.select("#tags-container").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

    function countSizeFunction(d) { return 10 + 40 * d.count / countExtent[1]; }
    function amountSizeFunction(d) {
        if (d.amount > 0) {
            return 10 + 40 * d.amount / amountExtent[1];
        }
    }

    function drawTemplate(data, sizeFunction) {
        function toPixelSize(d) {
            return sizeFunction(d) + "px";
        }
        
        function draw(data) {
            graph.selectAll("text").remove();
            
            graph.selectAll("text")
                .data(data).enter().append("text")
                .style("font-size", toPixelSize)
                .style("font-family", "Impact")
                .style("fill", function(d, i) { return fill(i); })
                .attr("text-anchor", "middle")
                .attr("transform", function(d) {
                    return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
                })
                .text(function(d) { return d.name; })
                .style("cursor", "pointer")
                .on("click", function(d) {
                    window.location = "/tracker/expenditures/search/?filter=" + d.name;
                });            
        }
        return function() {
            d3.layout.cloud().size([width + margin.left + margin.right,
                                             height + margin.top + margin.bottom])
                .rotate(function() { return ~~(Math.random() * 4) * 45 - 90; })
                .padding(2)
                .font("Impact")
                .fontSize(sizeFunction)
                .on("end", draw)
                .words(data)
                .start();
        };
    }
    
    $.ajax({
        url: getUrl('-count'),
        cache: false
    }).done(function(words) {
        if (words.length >= tagsThreshold) {
            countExtent = d3.extent(words, function(d) {
                return d.count;
            });
            countCloudBuilder = drawTemplate(words, countSizeFunction);
            
            document.getElementById('tags-container').style.display = "inline";

            countCloudBuilder();

            $('#amount-sort-btn').click(function () {
                if (amountCloudBuilder === undefined) {
                    $.ajax({
                        url: getUrl('-amount'),
                        cache: false
                    }).done(function(words) {
                        amountExtent = d3.extent(words, function(d) {
                            return d.amount;
                        });
                        amountCloudBuilder = drawTemplate(words, amountSizeFunction);
                        amountCloudBuilder();
                    });
                } else {
                    amountCloudBuilder();
                }
            });
            $('#count-sort-btn').click(function () {
                countCloudBuilder();
            });

        }
    });
}
