googleField = `<div class="form-group col-md-3 mx-auto">
                <label for="pages" class="m-4">Amount of Pages:</label>
                <input class="form-control" type="number" id="pages" name="pages" placeholder="Amount of pages">
            </div>
            <div class="queries">
                <div class="form-group col-md-6 mx-auto">
                    <label for="url" class="m-4">Query:</label>
                    <input class="form-control" type="text" id="url" name="query" placeholder="Enter query">
                </div>
            </div>
            <div class="form-group col-md-6 mx-auto">
                <button type="button" class="btn btn-primary m-4" onclick="createQueryField()">Add new query</button>
            <div class="m-4">
                <p>This method will search for your query in Google and scrape the results</p>
            </div>`;

customField = `<div class="form-group">
                <label for="url" class="m-4">URL:</label>
                <input class="form-control" type="text" id="url" name="query" placeholder="Enter URL">
            </div>
            <div class="m-4">
                <p>Enter URL for product and spider will scrape it</p>
            </div>`;



function showFields(source) {
    if (source === 'custom') {
        document.getElementById('fields').innerHTML = customField;
    } else if (source === 'google') {
        document.getElementById('fields').innerHTML = googleField;
    }
}

function send_request() {
    var form = document.getElementById('scrape-form');
    var formData = new FormData(form);
    var xml = new XMLHttpRequest();
    xml.open('POST', '/admin/product/scrape', true);
    xml.setRequestHeader('Content-Type', 'application/json');
    var queries = document.getElementsByName('query');
    var queryList = [];
    queries.forEach(query => {
        queryList.push(query.value);
    });
    var data = {
        'source': formData.get('source'),
        'query': queryList,
        'pages': formData.get('pages'),
    };
    
    formhtml = document.getElementById('fields').parentElement.innerHTML

    document.getElementById('fields').parentElement.innerHTML = `
    <div class="loader">
    <div class="lds-ring mt-5" id="loader-1"><div></div><div></div><div></div><div></div></div>
    <div>
        <p>Scraping... Please Wait.</p>
    </div>
    </div>    
    `;

    var jsonData = JSON.stringify(data);

    xml.onload = function() {
        if (this.status == 200) {
            var response = JSON.parse(this.responseText);
            alertmessage = document.getElementById('alert-messages');
            document.querySelector('.loader').parentElement.innerHTML = formhtml;
            if (response['status'] == 'success') {
                alertmessage.innerHTML
                    = `<div class="alert alert-success flash-close">
                    <div style="display: flex;">
                        <p style="margin: auto auto auto 0;">
                            ` + response['message'] + `
                        </p>
                        <button type="button" 
                        class="flash-close float-right" 
                        data-dismiss="alert" 
                        style="margin: auto 0 auto auto; background-color: transparent; border: none;"
                        onclick="this.parentElement.parentElement.style.display = 'none';"
                        >&times;</button>
                </div>`;
                } else {
                    alertmessage.innerHTML 
                    = `<div class="alert alert-danger flash-close">
                    <div style="display: flex;">
                        <p style="margin: auto auto auto 0;">
                            ` + response['message'] + `
                        </p>
                        <button type="button" 
                        class="flash-close float-right" 
                        data-dismiss="alert" 
                        style="margin: auto 0 auto auto; background-color: transparent; border: none;"
                        onclick="this.parentElement.parentElement.style.display = 'none';"
                        >&times;</button>
                </div>`;
                }
        }
    };

    xml.send(jsonData);
};


function createQueryField() {
    console.log('clicked');
    var div = document.querySelector('.queries');
    var field = `<div class="form-group col-md-6 mx-auto">
    <label for="url" class="m-4">Query:</label>
    <input class="form-control" type="text" id="url" name="query" placeholder="Enter query">
    </div>`
    div.innerHTML += field;
}
