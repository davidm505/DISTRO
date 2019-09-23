
clean(document.body);

let form = document.querySelector("form").addEventListener('submit', function(event) {

    let dict = {};

    completeForm = false;

    dict['ep'] = document.querySelector('#ep').value;
    dict['shootDay'] = document.querySelector("#shoot-day").value;
    dict['gb'] = document.querySelector("#gb").value;
    dict['cm'] = document.querySelector("#c-masters").value;
    dict['sm'] = document.querySelector("#s-masters").value;
    dict['email'] = 'complete';

    for ( key in dict) { 
        
        let value = dict[key];

        if (value == "") {
            alert("please fill out all fields!");
            completeForm = false;
            break;
        }
    }

    trt = trts();

    dict['trt'] = trt;

    console.log(dict);
    // event.preventDefault();
    
    if (completeForm == true) {

        $.post("/generator/complete/") + "3",
            {
                "ep": dict["ep"],
                "shoot_day": dict["shootDay"],
                "gb": dict["gb"],
                "cm": dict["cm"],
                "sm": dict["sm"],
                "test": ["david", "john"],
                "email": dict["email"]
            }, 
            function(response) {
                
                if (!response) {
                    alert("Hey there was no response!");
                }
                
                alert('Response back!');
            }
    }
});


let i = 2
function duplicate() {

    let ep = "ep-" + i;

    let trt = "trt-" + i;

    let ctrt = "ctrt-" + i;

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

    $(".trt-container").append($trtGroup);

    $($trtGroup).append($ep);

    $($trtGroup).append($trt);

    $($trtGroup).append($cTrt);

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


