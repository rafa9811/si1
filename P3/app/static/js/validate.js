function validateUsername() {
  var x = document.forms["fregistro"]["usuario"].value;
  if (x == "") {
    alert("El campo nombre debe estar relleno.");
    return false;
  }
}

function validatePassword() {
  var password = document.forms["fregistro"]["pwd1"].value;

  var re= /^(?=.*\d)(?=.*[A-Z]).{8,}$/;
  if (!re.test(password)){
    alert("La contraseña no cumple los estándares.");
    return false;
  }
}

function comparePasswords() {
  var password1 = document.forms["fregistro"]["pwd1"].value;
  var password2 = document.forms["fregistro"]["pwd2"].value;

  if (password1 != password2){
    alert("Las contraseñas no coinciden.");
    return false;
  }
}

function validateEmail() {
  var re = /^\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}$/
  var email = document.forms["fregistro"]["email"].value;
  if (!(re.test(email))){
    alert("La dirección de email es incorrecta.");
    return false;
  }
}

function validateCreditCard() {
  var card = document.forms["fregistro"]["tarjeta"].value;
  if (!(/^(?=.*\d).{12,}$/.test(card))){
    alert("La tarjeta no tiene doce dígitos.");
    return false;
  }
}

function validateForm() {
  var x = document.forms["fregistro"]["usuario"].value;
  var password1 = document.forms["fregistro"]["pwd1"].value;
  var password2 = document.forms["fregistro"]["pwd2"].value;
  var email = document.forms["fregistro"]["email"].value;
  var card = document.forms["fregistro"]["tarjeta"].value;
  if (x == "" || password1 == "" || password2 == "" || email == "" || card == ""){
    alert("No has rellenado todos los campos.");
    return false;
  }

  return true;
}
