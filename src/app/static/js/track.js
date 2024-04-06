var trackButtons = document.querySelectorAll('.track-button');
    trackButtons.forEach(button => {
        if (button.getAttribute('data-tracked') == 'True') {
            button.innerHTML = 'Tracked';
            button.classList.add('tracked');
        } else {
            button.innerHTML = 'Track';
            button.classList.add('track');
        }
    });


    function track(id) {
        
        var button = document.querySelector('.track-button[id="' + id + '"]');
        
        if (button.getAttribute('data-tracked') == 'True') {
            action = 'untrack';
            button.setAttribute('data-tracked', 'False');
            button.classList.remove('tracked');
            button.classList.add('track');
        } else {
            action = 'track';
            button.setAttribute('data-tracked', 'True');
            button.classList.remove('track');
            button.classList.add('tracked');
        } 
        // Make an AJAX request to the backend
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/cart/add', true);
        xhr.setRequestHeader('Content-Type', 'application/json');

        // Set the data to send in the request body
        var data = {
            'product_id': id, // The product ID to track
            'action': action // The action to perform
        };

        // Convert the data to JSON format
        var jsonData = JSON.stringify(data);

        // Handle the response from the backend
        xhr.onload = function() {
            if (xhr.status === 200) {
                // Request was successful
                var response = JSON.parse(xhr.responseText);
                if (response['status'] == 'success') {
                    console.log('successfully');
                    console.log(response['action']);
                    if (response['action'] == 'track') {
                        console.log('track');
                        button.classList.remove('track');
                        button.classList.add('tracked');
                        button.innerHTML = 'Tracked';
                    } else {
                        console.log('untrack');
                        button.classList.remove('tracked');
                        button.classList.add('track');
                        button.innerHTML = 'Track';
                    }
                } else {
                    console.error('Failed to track product');
                }
            } else {
                // Request failed
                console.error('Request failed. Status:', xhr.status);
            }
        };

        // Send the request
        xhr.send(jsonData);
    }


    let div = document.getElementById('args');
    document.getElementById('filters').addEventListener('click', function(event) {
        document.getElementById('args').classList.toggle('hidden');
    });