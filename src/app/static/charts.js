google.charts.load('current', {
    'packages':['geochart'],
    });
google.charts.load('current', {'packages':['table']});
google.charts.load('current', {'packages':['corechart']});

google.charts.setOnLoadCallback(drawRegionsMap);
google.charts.setOnLoadCallback(drawChart);
google.charts.setOnLoadCallback(routesTable);
google.charts.setOnLoadCallback(countriesTable);



function drawRegionsMap() {
var data = google.visualization.arrayToDataTable(country_sessions);

var options = {'color': 'rgb(234, 124, 124)',
    'width': '675px', 
    'height': '375px',
    'border-radius': 15,
    'background': ['rgb(234, 124, 124)', 'rgb(234, 124, 124)'],};

var chart = new google.visualization.GeoChart(document.getElementById('regions_div'));

chart.draw(data, options);
}



function drawChart() {

    var data = google.visualization.arrayToDataTable(user_devices);
    console.log(user_devices);

    var options = {
    title: 'Most used devices',
    };

    var chart = new google.visualization.PieChart(document.getElementById('piechart'));

    chart.draw(data, options);
}


function routesTable() {
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Page');
    data.addColumn('number', 'Views');
    data.addRows(routes);

    var table = new google.visualization.Table(document.getElementById('table_div_routes'));

    table.draw(data, {showRowNumber: true, width: '100%', height: '100%'});
}

function countriesTable() {
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'City');
    data.addColumn('number', 'Sessions');
    data.addRows(countries);
    
    var table = new google.visualization.Table(document.getElementById('table_div_countries'));
    
    table.draw(data, {showRowNumber: true, width: '100%', height: '100%'});
}
