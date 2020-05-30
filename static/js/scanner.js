
// Attach click event after everything has been loaded
document.addEventListener("DOMContentLoaded", function(){

    var objs = document.getElementsByClassName("update-health");
    for(var i = 0; i < objs.length; i++) {
        objs[i].addEventListener("click", function(e){
            e.preventDefault();
            scanUrl(event.target.dataset.url)
      });
    }
});

function scanUrl(url) {
    fetch('http://127.0.0.1:5000/api/scan?url=' + encodeURIComponent(url))
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(err => console.log(err))
}
