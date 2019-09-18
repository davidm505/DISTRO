let queryString = window.location.href;
let url = queryString.slice(-7);
let email = url.slice(5)
let id = url.slice(-1)

let form = document.querySelector("form").addEventListener('submit', function(event){

    event.preventDefault();

    let dict = {};

    dict["ep"] = document.querySelector("#ep").value;
    dict["shootDay"] = document.querySelector("#shoot-day").value;
    dict["gb"] = document.querySelector("#gb").value;
    dict["trt"] = document.querySelector("#trt").value;
    dict["cm"] = document.querySelector('#c-masters').value;
    dict["sm"] = document.querySelector("#s-masters").value;

    for (key in dict){

        let value = dict[key];
    
        console.log(key + value);
    
        if (value == ""){
            event.preventDefault();
            alert("Please fill out all fields!");
            break;
        }
    }

    $.post("/generator/" + url, 
    {"ep": dict["ep"],
    "shoot-day": dict["shootDay"],
    "gb": dict["gb"],
    "trt": dict["trt"],
    "c-masters": dict["cm"],
    "s-masters": dict["sm"]}, function(response){
        
        if (!response) {
            event.preventDefault();
            alert("Hey no response");
        }
        document.querySelector(".email-subject").innerHTML = response["subject"] + "<br>";
        let body = document.querySelector(".email-body");
        body.innerHTML = response["body"][0] + "<br>" + response["body"][1] + "<br><br>" + response["body"][2];

        document.querySelector(".email-distro").innerHTML = response["distro"];
    })

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