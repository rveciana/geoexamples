var jsdom = require('jsdom'); // Must be 3.x version, not 4.x, which doesn't work on nodejs npm install jsdom@3
var fs = require('fs');
var d3 = require('d3');
var topojson = require('topojson');


//http://www.ciiycode.com/0HNJNUPePjXq/jsdomenv-local-jquery-script-doesnt-work
jsdom.env({
        html: "<html><body></body></html>",
        //documentRoot: __dirname , doesn't seem to work
        scripts: [
          __dirname + '/node_modules/d3/d3.min.js'
        ],
        done:


  function (err, window) {

    var width = 900,
    height = 500;


    var projection = d3.geo.mercator();
    var path = d3.geo.path()
      .projection(projection);

    var svg = window.d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", height);

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
