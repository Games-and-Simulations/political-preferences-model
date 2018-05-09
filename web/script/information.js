
var INFORMATION = {
	
	loaded: 0,
	
	selectedCount: 0,

	voters: 0,
	
	lastSelected: false,
	okrsek: false,
	momc: false,
	obec: false,
	
	
	init: function(interaction) {
		this.registerControls(interaction);
		this.update();
	},
	
	registerControls: function(interaction) {
		$('div#controls input[type="radio"]').on('change', function(e) {
			interaction.changeSelectionMode();
		});
		$('div#models input[type="radio"]').on('change', function(e) {
			interaction.changeModel();
		});
	},
	
	readModelName: function() {
		return document.querySelector('input[name="model"]:checked').value;
	},
	
	readSelectionMode: function() {
		return document.querySelector('input[name="selection"]:checked').value;
	},
	
	setLoaded: function(num) {
		this.loaded = num;
		this.update();
	},

	setSelected: function(obec, momc, okrsek) {
		this.lastSelected = true;
		this.obec = obec;
		this.momc = momc;
		this.okrsek = okrsek;
		this.update();
	},
	
	unsetSelected: function() {
		this.lastSelected = false;
		this.update();
	},
	
	setSelectedCount: function(add, minus) {
		this.selectedCount += add - minus;
		this.update();
	},
	
	setVoters: function(num) {
		this.voters = num;
		this.update();
	},
	
	update: function() {
		document.getElementById("loaded").innerHTML = this.loaded;
		document.getElementById("selected").innerHTML = this.selectedCount;
		if (this.lastSelected) {
			var momc = this.momc;
			if (momc == 0) momc = "-"; 
			document.getElementById("lastselected").innerHTML = 'Obec: ' + this.obec 
				+ ' | Momc: ' + momc + ' | Okrsek: ' + this.okrsek;
		} else {
			document.getElementById("lastselected").innerHTML = '';
		}
		document.getElementById("population").innerHTML = this.voters;
	}	
	
}