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
        
        document.querySelector(".test").innerHTML = "HEy!";
        alert("Hey this worked!");
    })

})