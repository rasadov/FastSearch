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

var options = {
    'width': '1350px', 
    'height': '750px',
    'backgroundColor': '#222e3c',
    "colorAxis": {minValue: 0, colors: ['#183258', '#183243']}};

var chart = new google.visualization.GeoChart(document.getElementById('regions_div'));

chart.draw(data, options);
}



function drawChart() {
    var data = google.visualization.arrayToDataTable(user_devices);

    var options = {
        title: '',
        allowHtml: true,
        backgroundColor: '#222e3c',
        legend: {textStyle: {color: 'white', fontSize: 16}},
    };

    var chart = new google.visualization.PieChart(document.getElementById('piechart'));

    chart.draw(data, options);
}


function routesTable() {
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Page');
    data.addColumn('number', 'Views');
    data.addRows(routes);

    console.log(routes);

    var table = new google.visualization.Table(document.getElementById('table_div_routes'));
    var options = {allowHtml: true, showRowNumber: true,  width: '100%', height: '100%', backgroundColor: 'black'};
    

    table.draw(data, options);
}

function countriesTable() {
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'City');
    data.addColumn('number', 'Sessions');
    data.addRows(countries);
    

    var options = {allowHtml: true, showRowNumber: true,  width: '100%', height: '100%', color: 'black'};

    var table = new google.visualization.Table(document.getElementById('table_div_countries'));
    
    table.draw(data, options);
}
