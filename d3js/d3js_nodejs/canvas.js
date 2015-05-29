//cairo!!
//https://github.com/Automattic/node-canvas -> https://github.com/Automattic/node-canvas/wiki/_pages
// sudo apt-get install libcairo2-dev libjpeg8-dev libpango1.0-dev libgif-dev build-essential g++
var fs = require('fs');
var Canvas = require('canvas');
var d3 = require('d3');
var topojson = require('topojson');


var width = 900,
    height = 500;

var Image = Canvas.Image
  , canvas = new Canvas(width, height)
  , context = canvas.getContext('2d');


var projection = d3.geo.mercator();
var path = d3.geo.path()
  .projection(projection);


var data = JSON.parse(fs.readFileSync(__dirname +"/world-50m.json", 'utf8'));
var land = topojson.feature(data, data.objects.land);

  context.strokeStyle = '#888';
  context.fillStyle = '#aaa';

  context.beginPath();
  path.context(context)(land);
  context.fill();

  context.beginPath();
  path.context(context)(land);
  context.stroke();


var out = fs.createWriteStream(__dirname + '/test.png');
var stream = canvas.pngStream();
stream.on('data', function(chunk){
  out.write(chunk);
});

stream.on('end', function(){
  console.log('saved png');
});
