googleField = `<div class="form-group col-md-3 mx-auto">
                <label for="pages" class="m-4">Amount of Pages:</label>
                <input class="form-control" type="number" id="pages" name="pages" placeholder="Amount of pages">
            </div>
            <div class="form-group col-md-3 mx-auto">
                <label for="results_per_page" class="m-4">Results per Page:</label>
                <input class="form-control" type="number" id="results_per_page" name="results_per_page" placeholder="Results per page">
            </div>
            <div class="form-group col-md-6 mx-auto">
                <label for="url" class="m-4">Query:</label>
                <input class="form-control" type="text" id="url" name="query" placeholder="Enter query">
            </div>
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
