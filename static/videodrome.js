// $(document).ready(function() {
//     $("#navsearchinput").hide();
//     $("#navsearchbtn").hover(function() {
//         $("#navsearchinput").show();
//     });
// });


$(document).ready(function() {
    $("#navsearchinput").hide();
    $("#navsearchbtn").click(function() {
        $("#navsearchinput").toggle();
        $("#navsearchbtn").blur();
    });
});
