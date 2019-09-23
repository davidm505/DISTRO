let queryString = window.location.href;
let url = queryString.slice(-7);
let email = url.slice(5)
let id = url.slice(-1)


$(document).ready(function (){
    
    $(function () {
        $('[data-toggle="popover"').tooltip();
      })
})

let form = document.querySelector("form").addEventListener('submit', function(event){

    event.preventDefault()

    let emailSelect = document.querySelector(".custom-select");

    let dict = {};

    let completeForm = true;

    dict["ep"] = document.querySelector("#ep").value;
    dict["shootDay"] = document.querySelector("#shoot-day").value;
    dict["gb"] = document.querySelector("#gb").value;
    dict["trt"] = document.querySelector("#trt").value;
    dict["cm"] = document.querySelector('#c-masters').value;
    dict["sm"] = document.querySelector("#s-masters").value;
    dict["email"] = emailSelect.options[emailSelect.selectedIndex].text;

    // Check for any items in form that were not filled out.
    for (key in dict){

        let value = dict[key];
    
        if (value == ""){
            completeForm = false;
            break;
        }
    }

    if (completeForm == true) {

        $.post("/generator/" + dict["email"].toLowerCase() + "/" + id, 
        {
            "ep": dict["ep"],
            "shoot-day": dict["shootDay"],
            "gb": dict["gb"],
            "trt": dict["trt"],
            "c-masters": dict["cm"],
            "s-masters": dict["sm"],
            "test": ["john", "david"],
            "email": dict["email"]
        }, 
        function(response){
                
            if (!response) {
                event.preventDefault();
                alert("Hey no response");
            }
    
            // Display email contianer
            $('.email-container').fadeIn();
            document.querySelector(".email-container").style.display = "grid";
    
            document.querySelector(".email-subject").innerHTML = response["subject"] + "<br>";
            let body = document.querySelector(".email-body");
            body.innerHTML = response["body"][0] + "<br>" + response["body"][1] + "<br><br>" + response["body"][2];
    
            document.querySelector(".email-distro").innerHTML = response["distro"];
        })
    }


})

function copy(element) {

   if (window.getSelection) {
        var range = document.createRange();
         range.selectNode(document.querySelector(element));
         window.getSelection().removeAllRanges();
         window.getSelection().addRange(range);
         document.execCommand("copy");
         window.getSelection().removeAllRanges();
    }
};