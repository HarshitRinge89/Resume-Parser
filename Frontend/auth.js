let isLogin = true;

function toggleForm() {
  const title = document.getElementById("form-title");
  const switchText = document.querySelector(".switch");

  if (isLogin) {
    title.innerText = "Sign Up";
    switchText.innerHTML = `Already have an account? <span onclick="toggleForm()">Login</span>`;
  } else {
    title.innerText = "Login";
    switchText.innerHTML = `Don’t have an account? <span onclick="toggleForm()">Sign Up</span>`;
  }

  isLogin = !isLogin;
}

// Fake login (for now)
document.getElementById("auth-form").addEventListener("submit", function(e) {
  e.preventDefault();

  const username = document.getElementById("username").value;

  // store login locally
  localStorage.setItem("user", username);

  alert("Login successful!");

  // redirect
  window.location.href = "index.html";
});