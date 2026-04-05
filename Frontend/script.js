function checkLogin() {
  const isLoggedIn = localStorage.getItem("user");

  if (!isLoggedIn) {
    alert("Please login first!");
    window.location.href = "login.html";
  } else {
    window.location.href = "applicant.html";
  }
}