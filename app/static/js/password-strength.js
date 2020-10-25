function passwordStrength(password){
  var score = 0;
  if(password.length > 8){
    score +=1;
  }
  if(password.match(/[A-Z]/)){
    score += 1;
  }
  if(password.match(/[a-z]/)){
    score += 1;
  }
  if(password.match(/[0-9]/)){
    score += 1;
  }
  if(password.match(/.[!,@,#,$,%,^,&,*,?,_,~,-,(,)]/)){
    score += 1;
  }
  if(password.length > 10){
    score += 1;
  }
  return score;
}

$(document).ready(function(){
  $("#regPassword").keyup( function(){
    var password = $(this).val();
    var strength = passwordStrength(password);
    $(progress).attr("value", strength);
    $(progress).fadeTo(0, strength);
  });
});
