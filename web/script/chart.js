
var BARCHART = new Chart(document.getElementById("resultsChart"), {
	type: 'bar',
	data: {
		labels: ["other","ods","cssd","stan","kscm","zeleni","svobodni","pirati","top09","ano","kducsl","spd"],
		datasets: [
			{
				label: "snemovna2017",
				data: Array.apply(null, Array(12)).map(Number.prototype.valueOf, 0),
				backgroundColor: 'blue',
				borderColor: 'rgba(0,50,0,0.8)',
				borderWidth: 2,
				population: 0
			},
			{
				label: "model01",
				data: Array.apply(null, Array(12)).map(Number.prototype.valueOf, 0),
				backgroundColor: 'rgba(100,0,0,0.8)',
				borderColor: 'rgba(50,0,0,0.8)',
				borderWidth: 2,
				population: 0
			}]
	},
	options: {
		maintainAspectRatio: false,
		scales: {
			yAxes: [{
				display: true,
				ticks: {
					beginAtZero: true,
					steps: 10,
					stepValue: 5,
					max: 60
				}
			}]
		}
	}
});