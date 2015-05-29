var fs = require('fs');
var Canvas = require('canvas');
var d3 = require('d3');
var topojson = require('topojson');
var slug = require('slug');

//http://stackoverflow.com/questions/5050265/javascript-node-js-is-array-foreach-asynchronous
function processArray(items, process) {
    var todo = items.concat();

    setTimeout(function() {
        process(todo.shift());
        if(todo.length > 0) {
            setTimeout(arguments.callee, 25);
        }
    }, 25);
}

var width = 900,
    height = 500;


var data = JSON.parse(fs.readFileSync(__dirname +"/world-50m.json", 'utf8'));
var names = d3.tsv.parse(fs.readFileSync(__dirname +"/world-country-names.tsv", 'utf8'));

var land = topojson.feature(data, data.objects['land']);
var countries = topojson.feature(data, data.objects.countries);

countries = countries.features.filter(function(d) {
    return names.some(function(n) {
      if (d.id == n.id) return d.name = n.name;
    });
  }).sort(function(a, b) {
    return a.name.localeCompare(b.name);
  });


  processArray(countries, function (d) {
  console.info('Generating ' + d.id + ' -> ' + d.name );
  var bounds = d3.geo.bounds(d),
      dx = bounds[1][0] - bounds[0][0],
      dy = bounds[1][1] - bounds[0][1],
      x = (bounds[0][0] + bounds[1][0]) / 2,
      y = (bounds[0][1] + bounds[1][1]) / 2,
      scale = 20 / Math.max(dx / width, dy / height);

  var projection = d3.geo.equirectangular()
    .center(d3.geo.centroid(d))
    .scale(scale);

  var Image = Canvas.Image
      , canvas = new Canvas(width, height)
      , context = canvas.getContext('2d');

  var path = d3.geo.path()
        .projection(projection);

        context.strokeStyle = '#f00';
        context.fillStyle = '#aca';

        context.beginPath();
        path.context(context)(land);
        context.fill();

        context.fillStyle = '#f22';

        context.beginPath();
        path.context(context)(d);
        context.fill();

        context.beginPath();
        path.context(context)(d);
        context.stroke();

    var out = fs.createWriteStream('/tmp/' + slug(d.name) + '.png');
    var stream = canvas.pngStream();
    stream.on('data', function(chunk){
      out.write(chunk);
    });

    stream.on('end', function(){
      console.log('saved png');
    });
});
