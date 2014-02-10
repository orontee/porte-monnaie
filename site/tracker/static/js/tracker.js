var Tracker = {};

if(typeof String.prototype.trimRight !== 'function') {
  String.prototype.trimRight = function() {
    return this.replace(/\s+$/g, '');
  }
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
        if (value.length){
            target.value = value + ' ' + name;
        } else {
            target.value = name;
        }
    };
    for (var i = 0; i < nodes.length; i++){
        var node = nodes[i];
        node.addEventListener('click', listener);
    }
};
