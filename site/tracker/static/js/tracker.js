var Tracker = {};

if(typeof String.prototype.trimRight !== 'function') {
  String.prototype.trimRight = function() {
    return this.replace(/\s+$/g, '');
  };
}

Tracker.focus = function(id){
    var node = document.getElementById(id);
    if (node){
        node.focus();
    }
};

Tracker.listenToTags = function(id){
    var target = document.getElementById(id);
    var nodes = document.getElementsByClassName('tag');
    var listener = function(event){
        var name = event.target.innerHTML.trim();
        var value = target.value.trimRight();
        var node, i;
        if (value.length){
            target.value = value + ' ' + name;
        } else {
            target.value = name;
        }
    };
    for (i = 0; i < nodes.length; i++){
        node = nodes[i];
        node.addEventListener('click', listener);
    }
};
