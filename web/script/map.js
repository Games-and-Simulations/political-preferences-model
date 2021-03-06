

var VECTORLAYER = new ol.layer.Vector({
	source: new ol.source.Vector({
	}),
	style: new ol.style.Style({
	  stroke: new ol.style.Stroke({
		color: 'rgba(0, 0, 255, 1.0)',
		width: 2
	  })
	})
});

var DRAWLAYER = new ol.layer.Vector({
	source: new ol.source.Vector({
	}),
	style: new ol.style.Style({
	  stroke: new ol.style.Stroke({
		color: 'rgba(255, 0, 255, 1.0)',
		width: 3
	  })
	})
});

var MAP = new ol.Map({
	target: 'map',
	layers: [
		new ol.layer.Tile({
			source: new ol.source.OSM()
		}),
		VECTORLAYER,
		DRAWLAYER
	],
	view: new ol.View({
		projection: 'EPSG:3857',
		center: ol.proj.fromLonLat([14.30, 50.13]),
		zoom: 12,
		minZoom: 8
	})
});