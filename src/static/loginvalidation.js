$(document).ready(function(){

    $("form").submit(function(event){
        
        let userName = $("#username").val();
        let pW = $("#pw").val();

        if (!userName || !pW) {
            event.preventDefault();
            alert("Please double check the fields.");
        }
    });
});