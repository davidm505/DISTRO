let form = document.querySelector("form").addEventListener("submit", function(event) {
    let crewMemeber = {}
    crewMemeber['firstName'] = document.querySelector("#inputFirstName").value;
    crewMemeber['lastName'] = document.querySelector("#inputLastName").value;
    crewMemeber['email'] = document.querySelector("#inputEmail").value;
    crewMemeber['position'] = document.querySelector("#position").value;
    crewMemeber['department'] = document.querySelector("#inputDepartment").value;
    crewMemeber['breakDistro'] = document.querySelector('#break-distro').value;
    crewMemeber['completeDistro'] = document.querySelector("#complete-distro").value;
    crewMemeber['stillDistro'] = document.querySelector("#stills-distro").value;

    for(key in crewMemeber) {
        if(crewMemeber[key] == "" || crewMemeber[key] == "Choose...") {
            alert("Please fill out all fields!");
            event.preventDefault();
        }
    }
})