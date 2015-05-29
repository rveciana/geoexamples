var jsdom = require('jsdom');
var fs = require('fs');
var topojson = require('topojson');


jsdom.env({
        html: "<html><body></body></html>",
        scripts: [
          __dirname + '/node_modules/d3/d3.min.js'
        ],
        done:


  function (err, window) {

    var width = 900,
    height = 500;


    var projection = window.d3.geo.mercator();
    var path = window.d3.geo.path()
      .projection(projection);

    var svg = window.d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("xmlns", "http://www.w3.org/2000/svg");

    var data = JSON.parse(fs.readFileSync(__dirname +"/world-50m.json", 'utf8'));

    var land = topojson.feature(data, data.objects['land']);
      svg
        .datum(land)
        .append("path")
        .attr("class", "land")
        .style("fill","#aca")
        .style("stroke","#000")
        .attr("d", path);

      fs.writeFileSync("test.svg", window.d3.select("body").html());
      }
    });
