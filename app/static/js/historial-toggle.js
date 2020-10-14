$(document).ready(function(){
  $(".pedido").click(function(){
    $("#div" + $(this).attr('id')).toggle();
  });
});
