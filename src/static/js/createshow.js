let from = document.querySelector("form").addEventListener('submit', function(event) {

    let projectName = document.querySelector("#project-name").value;
    let projectCode = document.querySelector("#project-code").value;

    if (projectName == "" && projectCode == "") {
        event.preventDefault();
        alert("Please complete all fields!");
    }
})