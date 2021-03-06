var tim
var running = false
var apiUrl = 'http://127.0.0.1:5000/api'

document.addEventListener("DOMContentLoaded", function(){
    
    // Attach click event after everything has been loaded
    var objs = document.getElementsByClassName("update-health");
    for(var i = 0; i < objs.length; i++) {
        objs[i].addEventListener("click", function(e){
            e.preventDefault();
            checkHealth(e.target.dataset.id)
      });
    }

    document.getElementById('button-cleanup').addEventListener('click', cleanupDatabase)

    document.getElementById('scan-all').addEventListener('click', function(e) {
        e.preventDefault()
        if (running) {
            running = false
            clearInterval(tim)
            this.innerHTML = 'Check All '
        } else {
            running = true
            this.classList.add('running')
            this.innerHTML = 'Stop'
            checkAll()
        }
    })

    var deleteButtons = document.getElementsByClassName('js-remove')
    for(var i = 0; i < deleteButtons.length; i++) {
        deleteButtons[i].addEventListener('click', removeUrl)
    }

    var updateLinks = document.getElementsByClassName('js-update')
    for(var i = 0; i < updateLinks.length; i++) {
        updateLinks[i].addEventListener('click', updateUrl)
    }
});

function updateUrl(e) {
    e.preventDefault()
    var id = e.target.dataset.id
    var url = e.target.innerHTML
    var opts = {
        method: 'PUT',
        headers: {
            "Content-Type": 'application/json',
        },
        body: JSON.stringify({ url })
    }


    fetch(`${apiUrl}/url/${id}`, opts)
        .then(result => result.json())
        .then(data => {
            // let's update the URL for this row 
            if(data.updated && typeof data.updated_url === 'string') {
                document.getElementById('url-' + id).innerHTML = data.updated_url;
            } else if(data.removed) {
                document.getElementById('row-' + id).remove()
            }

            console.log(data)
            // var messageContainer = document.getElementById('message')
            // messageContainer.classList.remove('hidden')
        })
        .catch(err => {})


}

function removeUrl(e) {
    e.preventDefault()
    if(!confirm('Are you sure you want to remove this URL?'))
        return;
    var id = e.target.dataset.id
    document.getElementById('row-' + id).remove()
    fetch(`${apiUrl}/url/${id}`, {method: 'DELETE'})
        .then(result => result.json())
        .then(data => {
            console.log(data)
            // var messageContainer = document.getElementById('message')
            // messageContainer.classList.remove('hidden')
        })
        .catch(err => {})
}

function checkAll() {
    var currentIndex = 0;
    var rows = document.getElementsByClassName('url-row')
    var ids = []
    for(var i = 0; i < rows.length; i++) {
        ids.push(rows[i].dataset.id)
    }
    
    function checkNext() {
        if (!running) return; // stop!
        checkHealth(ids[(currentIndex % ids.length)])
            .then(() => {
                if(!running) return; // stop!
                currentIndex++
                tim = setTimeout(checkNext, 1000)
            })
            .catch(err => {
                clearTimeout(tim)
                console.log(err)
            })
    }
    checkNext()
}

function checkHealth(id) {
    document.getElementById('row-' + id).className = 'scanning'
    return fetch(`${apiUrl}/url/${id}/scan`)
        .then(response => response.json())
        .then(data => {
            // update status
            var status = document.getElementById('health-' + id)
            if(typeof data.error === 'string' && (data.error.match(/CERTIFICATE_VERIFY_FAILED/) || data.error.match(/SSLError/) || data.error.match(/HTTPSConnectionPool/) || data.error.match(/HTTPConnectionPool/))) { 
                status.innerHTML = ''
                status.className = 'health health-ssl-failed';
            } else {
                status.innerHTML = data.status_code
                status.className = 'health health-' + data.status_code
            }

            // update timestamp
            var tstamp = document.getElementById('last-update-' + id)
            tstamp.innerHTML = data.last_update

            // update possible redirect
            if(data.redirect_url) {
                document.getElementById('redirect-300-' + id).classList.add('active')
                document.getElementById('redirect-url-' + id).innerHTML = data.redirect_url;
            } else {
                document.getElementById('redirect-300-' + id).classList.remove('active')
            }

            document.getElementById('row-' + id).className = 'ready'
        })
}

function updateMessage(message) {
    var messageBox = document.getElementById('message-box')
    messageBox.classList.add('active')
    messageBox.innerHTML = message
}
function cleanupDatabase(e) {
    e.preventDefault() // don't submit any forms now... 

    if(!confirm('Are you sure you want to remove all of the records from the health_checks table?'))
        return

    fetch(`${apiUrl}/cleanup?confirmed=1`, { method: 'DELETE'})
        .then(result => result.json())
        .then(data => {
            updateMessage(data.message)
            console.log(data)
        })
        .catch(err => console.log(err))
}