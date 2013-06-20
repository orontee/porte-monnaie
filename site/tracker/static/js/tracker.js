var Tracker = {};

Tracker.toggle_menu = function(id) {
    var node = document.getElementById(id);
    if (node) {
        if (node.style.visibility == 'hidden') {
            node.style.visibility = 'visible';
        } else {
            node.style.visibility = 'hidden';
        }
    }
};
