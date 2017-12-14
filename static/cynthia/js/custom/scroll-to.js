$(document).ready(function (e) {
    $('#test').scrollToFixed();
    $('.res-nav_click').click(function () {
        $('.main-nav').slideToggle();
        return false
    });
});