var utils = {
	
	getPartyColorArray: function (partyNames, length) {
		var arr = [];
		for (var i = 0; i < length; i++) {
			arr.push(this.assignColorToParty(partyNames[i]));
		}
		return arr;
	},
	
	assignColorToParty: function (partyName) {
		switch(partyName) {
			case 'ano':
				return '#00FFFF';
			case 'kducsl':
				return '#FFFF00';
			case 'ods':
				return '#0000FF';
			case 'zeleni':
				return '#00FF00';
			case 'kscm':
				return '#FF0000';
			case 'cssd':
				return '#FFB500';
			case 'svobodni':
				return '#33207A';
			case 'spo':
			case 'spd':
				return '#808000';
			case 'stan':
				return '#C0C0C0';
			case 'other':
				return '#800080';
			case 'pirati':
				return '#000000';
			case 'top09':
				return '#851DBF';
			case 'usvit':
				return '#BF401D';
			default:
				return '#008080';
		}
	}
};