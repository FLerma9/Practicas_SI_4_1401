var root = location.pathname.split('.wsgi')[0]+'.wsgi';
root = root + '/ajaxRandom';
setInterval(function(){
    $("#numberUsers").load(root);
}, 3000);
