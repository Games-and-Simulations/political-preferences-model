
var INFORMATION = {
	
	loaded: 0,
		
	selected: false,
	okrsek: false,
	momc: false,
	obec: false,
		
	voters: 0,
	
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
		this.selected = true;
		this.obec = obec;
		this.momc = momc;
		this.okrsek = okrsek;
		this.update();
	},
	
	unsetSelected: function() {
		this.selected = false;
		this.update();
	},
	
	setVoters: function(num) {
		this.voters = num;
		this.update();
	},
	
	update: function() {
		document.getElementById("loaded").innerHTML = this.loaded;
		if (this.selected) {
			document.getElementById("selected").innerHTML = 'Obec: ' + this.obec 
				+ ' | Momc: ' + this.momc + ' | Okrsek: ' + this.okrsek;
		} else {
			document.getElementById("selected").innerHTML = '';
		}
		document.getElementById("population").innerHTML = this.voters;
	}	
	
}