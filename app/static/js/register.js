function validate(){
  var username = document.RegForm.username;
  var password = document.RegForm.regPassword;
  var passwordRep = document.RegForm.passwordRep;
  var credit =  document.RegForm.credit;
  var email = document.RegForm.email;
  var conditions = document.getElementById('conditions');

  if(validateUsername(username)){
    if(validatePassword(password, passwordRep)){
      if(validateCreditCard(credit)){
        if(validateEmail(email)){
          if(validateConds(conditions)){
            return true;
          }
        }
      }
    }
  }
  return false;
}

function validateUsername(username){
  var length = username.value.length;
  if(length == 0){
    alert("Username can't be empty");
    username.focus();
    return false;
  }
  if(username.value.match(/^[a-zA-z0-9]+$/)){
    return true;
  }
  else{
    alert("Username must be alphanumerical!");
    username.focus();
    return false;
  }
}

function validatePassword(password, passwordRep){
  var length = password.value.length;
  if(length == 0){
    alert("Password can't be empty");
    password.focus();
    return false;
  }
  else if( length < 8){
    alert("Password needs to be longer than 8 chars.");
    password.focus();
    return false;
  }
  if( password.value != passwordRep.value ){
    alert("Password dont match");
    passwordRep.focus();
    return false;
  }
  return true;
}

function validateCreditCard(credit){
  var length = credit.value.length;

  if(length == 0){
    alert("Credit Card field can't be empty");
    credit.focus();
    return false;
  }
  if( length > 18 || length < 13){
    alert("Credit card length should be between 13 and 18.");
    credit.focus();
    return false;
  }
  if(!credit.value.match(/^[0-9]+$/)){
    alert("Credit card must be numerical!");
    return false;
  }
  return true;
}

function validateEmail(email){
  var length = email.value.length;
  if(length == 0){
    alert("Email can't be empty");
    email.focus();
    return false;
  }
  if(email.value.match(/^\S+@\S+$/)){
    return true;
  }
  else{
    alert("Wrong email address, check @.");
    email.focus();
    return false;
  }
}

function validateConds(conditions){
  if(conditions.checked == true){
    return true;
  }
  alert("You need to agree the terms and conditions.");
  return false;
}
