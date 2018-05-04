
var DATALOADER = {
	
	interaction: false,
	information: false,
	
	init: function(interaction, information) {
		this.interaction = interaction;
		this.information = information;
	},
	
	changeChart: function (chart, identificationArray, datasetChangeFunction) {
		var dataLoader = this;
		
		this.getDataFromServer(chart, identificationArray, function () {
		
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
				
				dataLoader.performChartDataChange(chart, resultArray, datasetChangeFunction);
			}
			chart.update();
		});	
	},
	
	performChartDataChange: function(chart, resultArray, datasetChangeFunction) {
		for (var j = 0; j < resultArray.length; j++) {
			jsonObj = JSON.parse(resultArray[j]);
			
			if (jsonObj.type.startsWith("model")) {
				datasetChangeFunction(chart, jsonObj);
			}
			if (jsonObj.type.startsWith("snemovna")) {
				datasetChangeFunction(chart, jsonObj);
			}
		}
		this.information.setVoters(chart.data.datasets[0].population);
	},

	getDataFromServer: function (chart, identificationArray, callback) {
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
				modelid: this.interaction.model}),
			contentType: "application/json"
		}));
		
		// Wait for all ajax requests and then call the callback function
		// with server responses as arguments.
		$.when.apply($, requests).then(callback);
	},

	addToDataset: function (chart, jsonObj) {
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
	},

	deleteFromDataset: function (chart, jsonObj) {
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

}
