

$(document).ready(function (){

    clean(document.body);
    
    $(function () {
        $('[data-toggle="popover"').tooltip();
      })
})

let form = document.querySelector("form").addEventListener('submit', function(event) {

    event.preventDefault();

    let formAction = this.action;
    let dict = {};

    dict['ep'] = document.querySelector('#ep').value;
    dict['shootDay'] = document.querySelector("#shoot-day").value;
    dict['gb'] = document.querySelector("#gb").value;
    dict['email'] = 'complete';
    dict['shuttles'] = document.querySelector("#shuttles").value;
    
    // let validForm = validation(dict)
    
    dict['cm'] = document.querySelector("#c-masters").value;
    dict['sm'] = document.querySelector("#s-masters").value;
    dict['discrepancies'] = document.querySelector("#discrepancies").value;

    trt = trts();

    dict['trt'] = trt;

    console.log(dict);
    
    if (true) {

        $.post(formAction,
            {
                "ep": dict["ep"],
                "shoot-day": dict["shootDay"],
                "gb": dict["gb"],
                "c-masters": dict["cm"],
                "s-masters": dict["sm"],
                "email": dict["email"],
                "discrepancies": dict["discrepancies"],
                "shuttles": dict["shuttles"], 
                "trt": JSON.stringify(dict["trt"])
            }, 
            function(response) {
                
                if (!response) {
                    alert("Hey there was no response!");
                }
                
                // Display email contianer
                $('.email-container').fadeIn();
                document.querySelector(".email-container").style.display = "grid";
        
                document.querySelector(".email-subject").innerHTML = response["subject"] + "<br>";
                let body = document.querySelector(".email-body");
                body.innerHTML = response["body"];
        
                document.querySelector(".email-distro").innerHTML = response["distro"];               
            }
        )}
});


let i = 2
function duplicate() {

    let ep = "ep";

    let trt = "trt";

    let ctrt = "ctrt";

    let $trtGroup = $("<div/>", {
        id: "trt-group" + i
    });
    
    let $ep = $("<input/>", {
        type: "text",
        id: ep,
        name: ep,
        placeholder: "Episode"
    });

    let $trt = $("<input/>", {
        type: "text",
        id: trt,
        name: trt,
        placeholder: "Total Runtime"
    });

    let $cTrt = $("<input/>", {
        type: "text",
        id: ctrt,
        name: ctrt,
        placeholder: "Total Circle Runtime"
    });

    let $closeButton = $('<button/>', {
        type: "button",
        class: "close-button",
        'aria-label': "Close",
        onclick: "remove(this)"
    })

    $(".trt-container").append($trtGroup);

    $($trtGroup).append($ep);

    $($trtGroup).append($trt);

    $($trtGroup).append($cTrt);

    $($trtGroup).append($closeButton);

    $($closeButton).append("Remove");

    i++;
}

function clean(node) {

    for(let n = 0; n < node.childNodes.length; n++) {
        
        let child = node.childNodes[n];

        if (child.nodeType === 8 || child.nodeType === 3 && !/\S/.test(child.nodeValue)) {

            node.removeChild(child);
            n --;
        }
        else if(child.nodeType === 1) {

            clean(child);
        }
    }
}

function trts() {

    let c = document.querySelector(".trt-container").childNodes;

    let trtContainer = [];

    for (let i = 0; i < c.length; i++) {

        let grandChild = c[i].childNodes

        let dict = {};

        for (let j = 0; j < grandChild.length; j++) {
            
            if (grandChild[j].value != "")
                dict[grandChild[j].getAttribute('name')] = grandChild[j].value;
        }

        trtContainer[i] = dict;

    }

    return trtContainer; 
}

function validation(lst) {

    for ( key in lst) { 
        
        let value = lst[key];

        if (value == "") {
            alert("please fill out all fields!");
            return false;
        }
    }
    return true;
}

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

function remove(child) {

    let element = child.parentNode;

    let parent = child.parentNode.parentNode;

    parent.removeChild(element);
}
