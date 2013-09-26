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

Tracker.focus = function(id) {
    var node = document.getElementById(id);
    if (node) {
        node.focus();
    }
};
