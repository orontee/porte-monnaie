var Tracker = {};

if(typeof String.prototype.trimRight !== 'function') {
  String.prototype.trimRight = function() {
    return this.replace(/\s+$/g, '');
  };
}

Tracker.focus = function(id){
    var node = document.getElementById(id);
    if (node != null){
        node.focus();
    }
};

Tracker.activateParent = function(id){
    var node = document.getElementById(id);
    if (node != null){
        node.parentNode.className += 'active';
    }
};
