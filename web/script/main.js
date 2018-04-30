

Interaction.init(Information, electionBarChart);
loader.init(Information, Interaction, vectorLayer);

Interaction.addMap(map);

$('div#controls input[type="radio"]').on('change', function(e) {
	Interaction.changeSelectionMode();
});
$('div#models input[type="radio"]').on('change', function(e) {
	Interaction.changeModel();
});

Interaction.SelectClick.on('select', Interaction.selectionHandler, Interaction);

// When a polygon is drawn (and dispatches addfeature event),
// this event handler queries geoserver for shapes inside of it
// and selects them.
drawLayer.getSource().on('addfeature', function(e) {	
	var polygon = e.feature.getGeometry();
	loader.selectFeaturesInsideCoords(polygon, this);
}, drawLayer);

// Load features from the geoserver for the current map extent.
vectorLayer.setSource(new ol.source.Vector({
	format: new ol.format.GML3(),
	loader: function(extent, resolution, projection) {
		loader.loadFeaturesInExtent(extent);
	},
	strategy: ol.loadingstrategy.bbox
}));
