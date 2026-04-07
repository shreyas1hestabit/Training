/*document.getElementById("loginForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const loginId = document.getElementById("loginId").value.trim();
  const password = document.getElementById("loginPassword").value;
  const error = document.getElementById("loginError");

  error.textContent = "";

  if (loginId === "") {
    error.textContent = "Please enter Email or Mobile Number";
    return;
  }

  if (password.length < 6) {
    error.textContent = "Password must be at least 6 characters";
    return;
  }

  // ✅ SUCCESS (temporary)
  alert("Login successful!");
});*/

document.getElementById("loginForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const loginId = document.getElementById("loginId").value.trim();
  const password = document.getElementById("loginPassword").value;
  const error = document.getElementById("loginError");

  error.textContent = "";

  const savedUser = JSON.parse(localStorage.getItem("userData"));

  if (!savedUser) {
    error.textContent = "No account found. Please Sign In first.";
    return;
  }

  // email OR mobile match
  const isUserValid =
    (loginId === savedUser.email || loginId === savedUser.mobile) &&
    password === savedUser.password;

  if (!isUserValid) {
    error.textContent = "Invalid login credentials";
    return;
  }

  // ✅ LOGIN SUCCESS
  localStorage.setItem("isLoggedIn", "true");

  alert("Login successful!");

  // 👉 redirect to profile
  window.location.href = "profile.html";
});

