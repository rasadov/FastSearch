google.charts.load('current', {
    'packages':['geochart', 'table', 'corechart']
});

// Declare the variables at the top of your script
var routes, countries, user_devices, country_sessions;

function drawAllCharts() {
    drawRegionsMap(country_sessions);
    drawChart(user_devices);
    routesTable(routes);
    activeUsers(countries);
}

var xhrRoutes = new XMLHttpRequest();
xhrRoutes.open('GET', '/admin/analytics/page_views', true);
xhrRoutes.onreadystatechange = function() {
    if (xhrRoutes.readyState === 4 && xhrRoutes.status === 200) {
        var response = JSON.parse(xhrRoutes.responseText);
        routes = response;
        routes = routes.slice(0, 20);
        for (var i = 0; i < routes.length; i++) {
            routes[i][1] = parseInt(routes[i][1]);
        }
        document.getElementById('loader-1').remove();
        // Call the function to draw all charts
        google.charts.setOnLoadCallback(drawAllCharts);
    }
};
xhrRoutes.send();

var xhrCountries = new XMLHttpRequest();
xhrCountries.open('GET', '/admin/analytics/active_users', true);
xhrCountries.onreadystatechange = function() {
    if (xhrCountries.readyState === 4 && xhrCountries.status === 200) {
        var response = JSON.parse(xhrCountries.responseText);
        countries = response.sort(function(a, b) {
            return b[0].localeCompare(a[0]);
        });
        try {
            countries = countries.slice(0, 10);
        }
        catch (e) {
            console.log(e);
        }
        try {

            for (var i = 0; i < countries.length; i++) {
                countries[i][1] = parseInt(countries[i][1]);
                countries[i][0] = countries[i][0].replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3');
            }
        }
        catch (e) {
            console.log(e);
        }

        document.getElementById('loader-2').remove();
        try {

        // Call the function to draw all charts
        google.charts.setOnLoadCallback(drawAllCharts);
         }
        catch (e) {
            console.log(e);
        }
    }
};
xhrCountries.send();

var xhrUserDevices = new XMLHttpRequest();
xhrUserDevices.open('GET', '/admin/analytics/user_devices', true);
xhrUserDevices.onreadystatechange = function() {
    if (xhrUserDevices.readyState === 4 && xhrUserDevices.status === 200) {
        var response = JSON.parse(xhrUserDevices.responseText);
        user_devices = response;
        user_devices.unshift(['Device', 'Sessions']);
        // Call the function to draw all charts
        document.getElementById('loader-3').remove();
        google.charts.setOnLoadCallback(drawAllCharts);
    }
};
xhrUserDevices.send();

var xhrCountrySessions = new XMLHttpRequest();
xhrCountrySessions.open('GET', '/admin/analytics/country_sessions', true);
xhrCountrySessions.onreadystatechange = function() {
    if (xhrCountrySessions.readyState === 4 && xhrCountrySessions.status === 200) {
        var response = JSON.parse(xhrCountrySessions.responseText);
        country_sessions = response;
        country_sessions.unshift(['Country', 'Sessions']);
        // Call the function to draw all charts
        document.getElementById('loader-4').remove();
        google.charts.setOnLoadCallback(drawAllCharts);
    }
};
xhrCountrySessions.send();

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
    for (var i = 1; i < user_devices.length; i++) {
        user_devices[i][1] = parseInt(user_devices[i][1]);
    }
    var data = google.visualization.arrayToDataTable(user_devices);

    var options = {
        title: '',
        allowHtml: true,
        backgroundColor: '#222e3c',
        legend: {textStyle: {color: 'white', fontSize: 16}},
        pieSliceText: 'value',
        pieSliceTextStyle: {color: 'white', fontSize: 14},
    };

    var chart = new google.visualization.PieChart(document.getElementById('piechart'));

    chart.draw(data, options);
}

function routesTable(routes) {
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Page');
    data.addColumn('number', 'Views');
    data.addRows(routes);
    var table = new google.visualization.Table(document.getElementById('table_div_routes'));
    var options = {allowHtml: true, showRowNumber: true,  width: '100%', height: '100%', backgroundColor: 'black'};
    

    table.draw(data, options);
}

function activeUsers(active_users) {
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Date');
    data.addColumn('number', 'Users');
    data.addRows(active_users);
    

    var options = {allowHtml: true, showRowNumber: true,  width: '100%', height: '100%', color: 'black'};

    var table = new google.visualization.Table(document.getElementById('table_div_countries'));
    
    table.draw(data, options);
}
