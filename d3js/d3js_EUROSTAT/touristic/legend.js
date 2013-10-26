var legend = function(accessor){
    return function(selection){
      
      //Draw the legend for the map
      var legend = selection.append("g");
      var legendText = accessor.title;
      var numSquares = accessor.elements;
      var xLegend = 0;
      var yLegend = 0;
      var widthLegend = 400;
      
      var title_g = legend.append("g");
      var values_g = legend.append("g");
      
      var legendTitle = title_g.append("text")
        .text("Legend")
        .attr("font-family", "sans-serif")
        .attr("font-size", "18px")
        .attr("fill", "black");
        var bbox = legendTitle.node().getBBox();
        legendTitle.attr("x", xLegend + widthLegend/2 - bbox.width/2);
        legendTitle.attr("y", yLegend + 20);
        
      var legendTextEl = title_g.append("text")
        .text(legendText)
        .attr("y", yLegend + 75)
        .attr("font-family", "sans-serif")
        .attr("font-size", "14px")
        .attr("fill", "black");
      var bbox = legendTextEl.node().getBBox();
      legendTextEl.attr("x", xLegend + widthLegend/2 - bbox.width/2);

      for (i=0; i<numSquares; i++){
        values_g.append("rect")
          .attr("x", xLegend + (i+0.1*i/numSquares)*(widthLegend/numSquares))
          .attr("y", yLegend + 25)
          .attr("width", (widthLegend/numSquares)*0.9)
          .attr("height", 20)
          .attr("fill", color(accessor.domain[0] + i * accessor.domain[1]/(numSquares-1)));
        var value_text = values_g.append("text")
          .text(accessor.domain[0] + i * accessor.domain[1]/(numSquares-1))
          .attr("y", yLegend + 55)
          .attr("font-family", "sans-serif")
          .attr("font-size", "12px")
          .attr("fill", "black");
        var bbox = value_text.node().getBBox();
        value_text
          .attr("x", xLegend + (i+0.1*i/numSquares)*(widthLegend/numSquares) + (widthLegend/numSquares)*(0.9/2)- bbox.width/2);

      }
      var scale = accessor.width / 400;
      legend.attr("transform","translate("+accessor.posx+","+accessor.posy+") scale("+scale+") ");

};
};