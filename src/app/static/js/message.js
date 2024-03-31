var message_id = document.getElementById("message_id").innerHTML;

var xmr = new XMLHttpRequest();
xmr.open("POST", "/admin/message/mark_as_read", true);
xmr.setRequestHeader('Content-Type', 'application/json');
xmr.onload = function() {
    if (xmr.status === 200) {
        // Request was successful
        console.log('Message marked as read successfully');
    } else {
        // Request failed
        console.error('Request failed. Status:', xmr.status);
    }
};


console.log(message_id);

var data = {
    'message_id': message_id
    };

var json_data = JSON.stringify(data);

xmr.send(json_data);
