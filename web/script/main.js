
// INFORMATION connects program logic with DOM
INFORMATION.init(INTERACTION);

// INTERACTION takes care of user interaction with controls and the map (mostly feature selection)
INTERACTION.init(INFORMATION, BARCHART, DRAWLAYER, MAP, DATALOADER);

// DATALOADER object is used for downloading of election data 
// (both actual results and model prediction)
DATALOADER.init(INTERACTION, INFORMATION);

// LOADER object is used for downloading of geographical features
LOADER.init(INFORMATION, INTERACTION, VECTORLAYER);


// ----- Loading of geograpic features

// When a polygon is drawn (and dispatches addfeature event),
// this event handler queries geoserver for shapes inside of it
// and selects them.
DRAWLAYER.getSource().on('addfeature', function(e) {	
	var polygon = e.feature.getGeometry();
	LOADER.selectFeaturesInsideCoords(polygon, this);
}, DRAWLAYER);

// Load features from the geoserver for the current map extent.
VECTORLAYER.setSource(new ol.source.Vector({
	format: new ol.format.GML3(),
	loader: function(extent, resolution, projection) {
		LOADER.loadFeaturesInExtent(extent);
	},
	strategy: ol.loadingstrategy.bbox
}));

canvas = document.getElementById("resultsChart");


