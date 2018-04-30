
var loader = {
	// Communication with the Geoserver (Geographic data)

	init: function(information, interaction, targetLayer) {
		this.information = information;
		this.interaction = interaction;
		this.targetLayer = targetLayer;
		this.geoserverWFS = 'http://localhost:8080/geoserver/wfs?service=WFS&' +
			 'version=1.0.0&request=GetFeature&typeName=okrsek:'+ this.interaction.dbTableName +'&' +
			 'outputFormat=gml3&srsName=EPSG:3857&';
	},
	
	loadFeaturesInExtent: function(extent) {
		var url = 'http://localhost:8080/geoserver/wfs?service=WFS&' +
			'version=1.0.0&request=GetFeature&typeName=okrsek:'+ Interaction.dbTableName +'&' +
			'outputFormat=gml3&srsName=EPSG:3857&' +
			'bbox=' + extent.join(',') + ',EPSG:3857';
		var xhr = new XMLHttpRequest();
		xhr.open('GET', url);
		this.attachFeatureResponseOnload(xhr);
		xhr.send();
	},
	
	attachFeatureResponseOnload: function(xhr) {
		var thisObject = this;
		xhr.onload = function() {
			thisObject.processFeatureResponse(xhr);
		}
	},	
	
	processFeatureResponse: function(xhr) {
		if (xhr.status == 200) {
			var targetSource = this.targetLayer.getSource();
			var features = targetSource.getFormat().readFeatures(xhr.responseText);
			features.forEach(function e(item, index){
				item.setId(item.getProperties().id);
				item.isSelected = false;
				targetSource.addFeature(item);
			});
			// Update feature count
			this.information.setLoaded(targetSource.getFeatures().length);
		}
	},
	
	// This function queries geoserver for shapes inside of given polygon
	// and selects them. Afterwards it clears the callingLayer.
	selectFeaturesInsideCoords: function(polygon, callingLayer) {
		var coordString = this.coordsToString(polygon.getCoordinates()[0]);
		
		var featureString = '<PropertyName>geom</PropertyName>' +
		'<gml:Polygon gml:id="polygonrandomid" srsName="EPSG:3857" srsDimension="2">' +
			'<gml:outerBoundaryIs>' +
				'<gml:LinearRing>' +
					'<gml:coordinates>' + coordString + '</gml:coordinates>' +
				'</gml:LinearRing>' +
			'</gml:outerBoundaryIs>' +
		'</gml:Polygon>';
		var request = '<Within>' + featureString + '</Within>';
		var filter = '<Filter xmlns:gml="http://www.opengis.net/gml">' + request + '</Filter>';
		var url = this.geoserverWFS + 'propertyName=id&filter=' + filter;

		var xhr = new XMLHttpRequest();
		xhr.open('GET', url);
		this.attachFilterResponseOnload(xhr, callingLayer);
		xhr.send();		
	},
	
	attachFilterResponseOnload: function(xhr, callingLayer) {
		var thisObject = this;
		xhr.onload = function() {
			thisObject.processFilterResponse(xhr, callingLayer);
		}
	},
	
	// This function reads feature Ids from the server response,
	// finds these features in targetLayer and selects them.
	// Then it clears the drawn polygon.
	processFilterResponse: function(xhr, callingLayer) {
		if (xhr.status == 200) {
			var targetSource = this.targetLayer.getSource();
			var featureIds = targetSource.getFormat().readFeatures(xhr.responseText);
			var featuresToBeSelected = [];
			
			featureIds.forEach(function (item, index){
				var id = item.getProperties().id;
				var feature = targetSource.getFeatureById(id);
				if (feature != null) {
					// feature is already loaded in vector layer
					if (!feature.isSelected) {
						// feature is not yet selected - prepare it for selection
						featuresToBeSelected.push(feature);
					}
				}
			});
			this.selectAllGivenFeatures(featuresToBeSelected);
			// Clear the layer
			callingLayer.getSource().clear();
		}
	},
	
	selectAllGivenFeatures: function(featuresToBeSelected) {
		alreadySelected = this.interaction.SelectClick.getFeatures();
		featuresToBeSelected.forEach(function (item) {
			alreadySelected.push(item);
		});
		this.interaction.SelectClick.dispatchEvent({
			type: 'select',
			selected: featuresToBeSelected,
			deselected: []
		});	
	},
	
	// Return coords as string with whitespace as delimiter.
	coordsToString: function(coords) {
		var coordString = '';
		for (var i = 0; i < coords.length; i++) {
			coordString += coords[i] + ' ';
		}		
		return coordString;
	}
	
}




