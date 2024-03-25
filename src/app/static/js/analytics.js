google.charts.load('current', {
    'packages':['geochart', 'table', 'corechart']
});

// Declare the variables at the top of your script
var routes, countries, user_devices, country_sessions;

function drawAllCharts() {
    drawRegionsMap(country_sessions);
    drawChart(user_devices);
    routesTable(routes);
    countriesTable(countries);
}

var xhr = new XMLHttpRequest();
xhr.open('GET', '/admin/analytics/data', true);
xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
        var response = JSON.parse(xhr.responseText);
        routes = response.page_views;
        countries = response.country_sessions;
        user_devices = response.user_devices;
        country_sessions = response.country_sessions;
        country_sessions.unshift(['Country', 'Sessions']);

        user_devices.unshift(['Device', 'Sessions']);

        routes = routes.slice(0, 15);

        console.log("Data received successfully");
        for (var i = 0; i < routes.length; i++) {
            routes[i][1] = parseInt(routes[i][1]);
        }
        for (var i = 1; i < countries.length; i++) {
            countries[i][1] = parseInt(countries[i][1]);
        }
        // Call the function to draw all charts
        google.charts.setOnLoadCallback(drawAllCharts);
    }
};
xhr.send();

function drawRegionsMap(country_sessions) {
var data = google.visualization.arrayToDataTable(country_sessions);

var options = {
    'width': '1350px', 
    'height': '750px',
    'backgroundColor': '#222e3c',
    "colorAxis": {minValue: 0, colors: ['#fff', '#183243']}
};

var chart = new google.visualization.GeoChart(document.getElementById('regions_div'));

chart.draw(data, options);
}



function drawChart(user_devices) {
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


function routesTable(routes) {
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Page');
    data.addColumn('number', 'Views');
    data.addRows(routes);

    console.log(routes);

    var table = new google.visualization.Table(document.getElementById('table_div_routes'));
    var options = {allowHtml: true, showRowNumber: true,  width: '100%', height: '100%', backgroundColor: 'black'};
    

    table.draw(data, options);
}

function countriesTable(countries) {
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'City');
    data.addColumn('number', 'Sessions');
    data.addRows(countries);
    

    var options = {allowHtml: true, showRowNumber: true,  width: '100%', height: '100%', color: 'black'};

    var table = new google.visualization.Table(document.getElementById('table_div_countries'));
    
    table.draw(data, options);
}
