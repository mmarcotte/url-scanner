var tim

document.addEventListener("DOMContentLoaded", function(){
    
    // Attach click event after everything has been loaded
    var objs = document.getElementsByClassName("update-health");
    for(var i = 0; i < objs.length; i++) {
        objs[i].addEventListener("click", function(e){
            e.preventDefault();
            checkHealth(event.target.dataset.id)
      });
    }

    document.getElementById('scan-all').addEventListener('click', function(e) {

        e.preventDefault()
        if (e.target.className === 'running') {
            document.getElementById('scan-all').innerHTML = 'Scan All'
            document.getElementById('scan-all').className = 'btn'
            clearInterval(tim)
        } else {
            document.getElementById('scan-all').innerHTML = 'Stop'
            document.getElementById('scan-all').className = 'btn running'
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
        checkHealth(ids[(currentIndex % ids.length)])
            .then(() => {
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
            var obj = document.getElementById('health-' + id)
            obj.innerHTML = data.status_code
            obj.className = 'health health-' + data.status_code
            document.getElementById('row-' + id).className = 'ready'
        })
}
