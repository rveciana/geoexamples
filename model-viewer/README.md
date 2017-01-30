This example shows how to draw streamlines for a vectorial field using d3js and Canvas.

To calculate the streamlines, the [raster-streamlines library](https://github.com/rveciana/raster-streamlines) is used. To calculate the position of the small arrows at the middle of each line, the [svg-path-properties library](https://github.com/rveciana/svg-path-properties) is used too.

The data is the wind from a sample WRF model, reprojected from Lambert Conformal to latlon so it can be drawn.

The wind speed is plotted under the barbs, using the [d3-marching-squares](https://github.com/rveciana/d3-marching-squares) library.
