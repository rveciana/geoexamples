This example belongs to the GeoExamples blog http://geoexamples.blogspot.com/2013/10/using-eurostats-data-with-d3js.html


The [NUTS classification](http://epp.eurostat.ec.europa.eu/portal/page/portal/nuts_nomenclature/introduction) (Nomenclature of territorial units for statistics) is a hierarchical system for dividing up the economic territory of the EU. MAny of the EUROSTAT data is relative to these regions, and this data is a good candidate to be mapped.

The problem is that EUROSTAT provides [some shapefiles](http://epp.eurostat.ec.europa.eu/portal/page/portal/gisco_Geographical_information_maps/popups/references/administrative_units_statistical_units_1) in one hand, but without the actual names for the regions, nor other information, and [some tables](http://ec.europa.eu/eurostat/ramon/documents/nuts/NUTS_2010.zip) with the name and population for every region. This data has to be joined to be able to map properly.

In this example, the [criminality data](http://epp.eurostat.ec.europa.eu/portal/page/portal/crime/data/database) has been represented. Since the data gives absolute values for regions that have different sizes and populations, the map represents the number of crimes for every 100000 inhabitants. The values from the scale go from 0 (dark blue) to 5 (bright red).