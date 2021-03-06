
var INTERACTION = {
	
	mode: 'click',
	model: '01',
	chart: false,
	information: false,
	dataLoader: false,
	
	init: function(info, chart, drawInputLayer, map, dataLoader) {
		this.information = info;
		this.chart = chart;
		this.dataLoader = dataLoader;
		this.Polygon = new ol.interaction.Draw({
			source: drawInputLayer.getSource(),
			type: 'Polygon'			
		});
		this.registerMap(map);
		this.registerControls();
		this.changeSelectionMode();
		this.SelectClick.on('select', this.selectionHandler, this);
	},
	
	registerMap: function(map) {
		map.addInteraction(this.Polygon);
		map.addInteraction(this.SelectClick);
	},
	
	registerControls: function() {
		var interaction = this;
		
		var modelNameSelector = this.information.getModelNameSelector();
		$(modelNameSelector).on('change', function(e) {
			interaction.changeModel();
		});
		
		var selectionModeSelector = this.information.getSelectionModeSelector();
		$(selectionModeSelector).on('change', function(e) {
			interaction.changeSelectionMode();
		});
	},
	
	changeModel: function() {
		var currentSelection = this.SelectClick.getFeatures().getArray();
		
		// deselect all in the old model
		this.SelectClick.dispatchEvent({
			type: 'select',
			selected: [],
			deselected: currentSelection
		});
		
		// change model
		this.model = this.information.readModelName();
		
		// select all with the new model
		this.SelectClick.dispatchEvent({
			type: 'select',
			selected: currentSelection,
			deselected: []
		});
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
		// When features are selected (deselected), add (remove) their results to (from) the chart
		
		if (e.selected.length > 0) {
			var identificationArray = [];
			for (var i = 0; i < e.selected.length; i++) {
				// mark it as selected so it cannot be selected more than once
				e.selected[i].isSelected = true;
				var keys = e.selected[i].getProperties();
				identificationArray.push([keys.obec, keys.momc, keys.okrsek]);
			}
			this.dataLoader.changeChart(this.chart, identificationArray, this.dataLoader.addToDataset);
		}
		
		if (e.deselected.length > 0) {
			var identificationArray = [];
			for (var i = 0; i < e.deselected.length; i++) {
				e.deselected[i].isSelected = false;
				var keys = e.deselected[i].getProperties();
				identificationArray.push([keys.obec, keys.momc, keys.okrsek]);
			}	
			this.dataLoader.changeChart(this.chart, identificationArray, this.dataLoader.deleteFromDataset);
		}
		
		if (e.selected.length == 1 && this.mode == 'click') {
			// record info of the last selected feature
			var keys = e.selected[0].getProperties();
			this.information.setSelected(keys.obec, keys.momc, keys.okrsek);
		}
		// record the number of selected features
		this.information.setSelectedCount(e.selected.length, e.deselected.length);
	}
	
};
