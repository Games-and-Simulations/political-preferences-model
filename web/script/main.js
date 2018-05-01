
// INFORMATION connects program logic with DOM
INFORMATION.init(INTERACTION);

// INTERACTION takes care of user interaction with controls and the map (mostly feature selection)
INTERACTION.init(INFORMATION, electionBarChart, drawLayer, map, DATALOADER);

// DATALOADER object is used for downloading of election data 
// (both actual results and model prediction)
DATALOADER.init(INTERACTION, INFORMATION);

// LOADER object is used for downloading of geographical features
LOADER.init(INFORMATION, INTERACTION, vectorLayer);


// ----- Loading of geograpic features

// When a polygon is drawn (and dispatches addfeature event),
// this event handler queries geoserver for shapes inside of it
// and selects them.
drawLayer.getSource().on('addfeature', function(e) {	
	var polygon = e.feature.getGeometry();
	LOADER.selectFeaturesInsideCoords(polygon, this);
}, drawLayer);

// Load features from the geoserver for the current map extent.
vectorLayer.setSource(new ol.source.Vector({
	format: new ol.format.GML3(),
	loader: function(extent, resolution, projection) {
		LOADER.loadFeaturesInExtent(extent);
	},
	strategy: ol.loadingstrategy.bbox
}));

