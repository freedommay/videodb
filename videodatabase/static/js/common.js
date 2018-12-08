$(document).ready(function () {
    var s = window.location.pathname;

    var r = s.match("[a-z|A-Z]*/$");
    var t = r.toString();
    var n = t.match("[a-z|A-Z]*");
    var d = n.toString();
    if (document.getElementById(d) != null) {
        document.getElementById(d).style.color = "red";
    }
});