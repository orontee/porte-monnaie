var Tracker = {};

Tracker.toggleMenu = function(id) {
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

Tracker.listenToTags = function(id) {
    var target = document.getElementById(id);
    if (target) {
        var nodes = document.getElementsByClassName('tag');
        for (var i = 0; i < nodes.length; i++) {
            var node = nodes[i];
            node.onclick = function(n) {
                return function() {
                    var value = target.value.trimRight();
                    if (value.length) {
                        target.value = value + ' ' + n.innerHTML.trim();
                    } else {
                        target.value = n.innerHTML.trim();
                    }
                };
            }(node);
        }
    }
};
