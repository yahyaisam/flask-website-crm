// Task 2
const month = Object.keys(deals_obj);
const values = Object.values(deals_obj);

new Chart("deals_per_month", {
	type: "line", // line chart
	data: {
		labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
		datasets: [{
			fill: false, // leaves it blank under the graph lines
			lineTension: 0, // straight lines between dots
			backgroundColor: "#13CF16", // color of the dots
			borderColor: "#b2dc6c", // color of the lines
			data: values,
			label: "Number of Won Deals Per Month Last Year"
		}]
	},
});



// Task 3
var company_name = Object.keys(won_deals_obj);
var deal_values = Object.values(won_deals_obj);

// gets values from line 39
var barColors = [];

deal_values.forEach(function(item) {
	// random rgb value between 0 and 255
	var red = Math.floor(Math.random() * 256);
    var green = Math.floor(Math.random() * 256);
    var blue = Math.floor(Math.random() * 256);

	var rgb = 'rgb(' + red + ', ' + green + ', ' + blue + ')';
	barColors.push(rgb)
})

new Chart("deals_per_company", {
	type: "horizontalBar", // bar chart
	data: {
		labels: company_name,
		datasets: [{
			backgroundColor: barColors,
			data: deal_values,
		}]
	},
	options: {
		indexAxis: 'yAxis',
		legend: {
			display: false, // hide rectangle thingy
		}
	}
});
