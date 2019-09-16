let form = document.querySelector("main form").addEventListener("submit", function(event){
    
    let email = document.querySelector("#email");
    let pw = document.querySelector("#pw");

    let pwValue = pw.value;
    let emailValue = email.value;

    if (!pwValue || !emailValue) {
        event.preventDefault();
        alert("Please check the fields below.");
    }
});