var tim
var running = false

document.addEventListener("DOMContentLoaded", function(){
    
    // Attach click event after everything has been loaded
    var objs = document.getElementsByClassName("update-health");
    for(var i = 0; i < objs.length; i++) {
        objs[i].addEventListener("click", function(e){
            e.preventDefault();
            checkHealth(event.target.dataset.id)
      });
    }

    var checkAllButton = document.getElementById('scan-all')
    .addEventListener('click', function(e) {
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

});

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
    return fetch('http://127.0.0.1:5000/api/scan/' + id)
        .then(response => response.json())
        .then(data => {
            // update status
            var status = document.getElementById('health-' + id)
            status.innerHTML = data.status_code
            status.className = 'health health-' + data.status_code

            // update timestamp
            var tstamp = document.getElementById('last-update-' + id)
            tstamp.innerHTML = data.last_update

            document.getElementById('row-' + id).className = 'ready'
        })
}
