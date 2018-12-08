function showname(a) {
    document.getElementById(a).style.opacity = 0.5;
    document.getElementsByName(a)[0].style.visibility = "visible";
    $('div[name=a]').fadeIn();
}
function closename(a) {
    document.getElementById(a).style.opacity = 1.0;
    document.getElementsByName(a)[0].style.visibility = "hidden";
 }