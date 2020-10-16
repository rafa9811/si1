function lvalidateForm() {
  var x = document.forms["flogin"]["lusuario"].value;
  if (x == "") {
    alert("El campo usuario debe estar relleno.");
    return false;
  }
}

function lvalidatePassword() {
  var password = document.forms["flogin"]["lpwd"].value;
  if (password == "") {
    alert("El campo contraseña debe estar relleno.");
    return false;
  }
}
