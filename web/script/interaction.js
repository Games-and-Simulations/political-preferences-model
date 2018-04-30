
var Interaction = {
	
	dbTableName: 'publish',
	mode: 'click',
	chart: false,
	information: false,
	model: '01',
	
	init: function(info, chart) {
		this.information = info;
		this.chart = chart;
		this.changeSelectionMode();
	},
	
	changeModel: function() {
		this.model = information.readModelName();
	},
	
	changeSelectionMode: function() {
		this.mode = this.information.readSelectionMode();
		if (this.mode == "click") {
			this.Polygon.setActive(false);
			this.SelectClick.setActive(true);
		} else if (this.mode == "polygon") { 
			this.SelectClick.setActive(false);	
			this.Polygon.setActive(true);					
		}
	},
	
	addMap: function(map) {
		map.addInteraction(this.Polygon);
		map.addInteraction(this.SelectClick);
	},
	
	Polygon: new ol.interaction.Draw({
		source: drawLayer.getSource(),
		type: 'Polygon'
	}),

	SelectClick: new ol.interaction.Select({
		condition: ol.events.condition.click,
		style: new ol.style.Style({
			stroke: new ol.style.Stroke({
				color: 'rgba(255,0,0,1.0)',
				width: 4
			})
		}),
	}),
	
	selectionHandler: function(e) {
		
		if (e.selected.length > 0) {
			var identificationArray = [];
			for (var i = 0; i < e.selected.length; i++) {
				// mark it as selected so it cannot be selected more than once
				e.selected[i].isSelected = true;
				var keys = e.selected[i].getProperties();
				identificationArray.push([keys.obec, keys.momc, keys.okrsek]);
			}
			changeChart(this.chart, identificationArray, addToDataset);
		}
		
		if (e.deselected.length > 0) {
			var identificationArray = [];
			for (var i = 0; i < e.deselected.length; i++) {
				e.deselected[i].isSelected = false;
				var keys = e.deselected[i].getProperties();
				identificationArray.push([keys.obec, keys.momc, keys.okrsek]);
			}	
			changeChart(this.chart, identificationArray, deleteFromDataset);
		}
		if (e.selected.length == 1 && Interaction.mode == 'click') {
			// record info of the last selected feature
			var keys = e.selected[0].getProperties();
			this.information.setSelected(keys.obec, keys.momc, keys.okrsek);
		}
	}
	
};

function callToDatabase(chart, identificationArray, callback) {
	var requests = [];
	
	requests.push($.ajax({
		type: "POST",
		url: "get-result2017-bulk.php",
		data: JSON.stringify({idArray: identificationArray}),
		contentType: "application/json"		
	}));
	requests.push($.ajax({
		type: "POST",
		url: "get-prediction-bulk.php",
		data: JSON.stringify({idArray: identificationArray,
			modelid: Interaction.model}),
		contentType: "application/json"
	}));
	
	// Wait for all ajax requests and then call callback function
	// with server responses as arguments.
	$.when.apply($, requests).then(callback);
}

function addToDataset(chart, jsonObj) {
	// Add data from json object to the chart.
	var dataset;
	chart.data.datasets.forEach(function (set) {
		if (set.label == jsonObj.type) {
			dataset = set;
		}
	});
	var prevPopulation = dataset.population;
	var currPopulation = jsonObj["pocet_volicu"];
	for (var i = 0; i < chart.data.labels.length; i++) {
		// Add data weighted by population
		dataset.data[i] = Math.abs((dataset.data[i] * prevPopulation + 
			jsonObj[chart.data.labels[i]] * currPopulation) / (prevPopulation + currPopulation));
	}
	dataset.population = prevPopulation + currPopulation;
}

function deleteFromDataset(chart, jsonObj) {
	var dataset;
	chart.data.datasets.forEach(function (set) {
		if (set.label == jsonObj.type) {
			dataset = set;
		}
	});
	var prevPopulation = dataset.population;
	var currPopulation = jsonObj["pocet_volicu"];
	if (prevPopulation - currPopulation == 0) {
		dataset.data = Array.apply(null, Array(chart.data.labels.length)).map(Number.prototype.valueOf, 0);
	} else {
		for (var i = 0; i < chart.data.labels.length; i++) {
			dataset.data[i] = Math.abs((dataset.data[i] * prevPopulation - 
				jsonObj[chart.data.labels[i]] * currPopulation) / (prevPopulation - currPopulation));
		}
	}
	dataset.population = prevPopulation - currPopulation;
}

function changeChart(chart, identificationArray, datasetChangeFunction) {
	callToDatabase(chart, identificationArray, function () {
		for (var i = 0; i < arguments.length; i++) {
			var response;
			// response from server has 3 items (first being response text), therefore if we only have one request, we are only interested
			// in first field. When there are more requests, it comes packed as array of groups of 3 items (one group per request),
			// so we take first field of each such array
			if (arguments[0] instanceof Array) {
				// there are multiple requests
				response = arguments[i][0];
			} else {
				// there is only one request, that means response text is on index 0
				if (i > 0) {break;}
				response = arguments[0];
			}
			resultArray = JSON.parse(response).resultArray;
			
			for (var j = 0; j < resultArray.length; j++) {
				jsonObj = JSON.parse(resultArray[j]);

				if (jsonObj.type.startsWith("model")) {
					datasetChangeFunction(chart, jsonObj);
				}
				if (jsonObj.type.startsWith("snemovna")) {
					datasetChangeFunction(chart, jsonObj);
				}
			}
			Information.setVoters(chart.data.datasets[0].population);
		}
		chart.update();
	});	
}

