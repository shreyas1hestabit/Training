const isLoggedIn = localStorage.getItem("isLoggedIn");
const user = JSON.parse(localStorage.getItem("userData"));

if (!isLoggedIn || !user) {
  window.location.href = "login.html";
}

document.getElementById("name").textContent =
  user.firstName + " " + user.lastName;

document.getElementById("dob").textContent = user.dob;
document.getElementById("mobile").textContent = user.mobile;
document.getElementById("email").textContent = user.email;

document.getElementById("address").textContent =
  `${user.address1} ${user.address2} ${user.address3}`;

document.getElementById("logoutBtn").addEventListener("click", () => {
  localStorage.removeItem("isLoggedIn");
  window.location.href = "login.html";
});
