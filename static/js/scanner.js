
// Attach click event after everything has been loaded
document.addEventListener("DOMContentLoaded", function(){

    var objs = document.getElementsByClassName("update-health");
    for(var i = 0; i < objs.length; i++) {
        objs[i].addEventListener("click", function(e){
            e.preventDefault();
            checkHealth(event.target.dataset.id)
      });
    }
});

function checkHealth(id) {
    fetch('http://127.0.0.1:5000/api/scan/' + id)
        .then(response => response.json())
        .then(data => {
            var obj = document.getElementById('health-' + id)
            obj.innerHTML = data.health
            obj.className = 'health health-' + data.health
        })
        .catch(err => console.log(err))
}
