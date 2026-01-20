/*document.getElementById("signupForm").addEventListener("submit", function (e) {
  e.preventDefault(); // ❌ form submit roko

  const mobile = document.getElementById("mobile").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const confirmPassword = document.getElementById("confirmPassword").value;
  const terms = document.getElementById("terms").checked;
  const errorMsg = document.getElementById("errorMsg");

  errorMsg.style.color = "red";
  errorMsg.textContent = "";

  // ✅ Mobile validation (10 digits only)
  if (!/^\d{10}$/.test(mobile)) {
    errorMsg.textContent = "Mobile number must be exactly 10 digits";
    return;
  }

  // ✅ Email validation
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    errorMsg.textContent = "Please enter a valid email address";
    return;
  }

  // ✅ Password length
  if (password.length < 6) {
    errorMsg.textContent = "Password must be at least 6 characters long";
    return;
  }

  // ❌ Password mismatch
  if (password !== confirmPassword) {
    errorMsg.textContent = "Password and Confirm Password do not match";
    return;
  }

  // ❌ Terms unchecked
  if (!terms) {
    errorMsg.textContent = "Please accept Terms & Conditions";
    return;
  }

  // ✅ SUCCESS
  alert("Account created successfully!");
  e.target.reset();
});*/

document.getElementById("signupForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const form = e.target;

  const userData = {
    firstName: form.querySelector('input[placeholder="First Name *"]').value,
    lastName: form.querySelector('input[placeholder="Last Name *"]').value,
    dob: form.querySelector('input[type="date"]').value,
    mobile: document.getElementById("mobile").value,
    email: document.getElementById("email").value,
    password: document.getElementById("password").value,
    address1: form.querySelector('textarea[placeholder="Address Line 1"]').value,
    address2: form.querySelector('textarea[placeholder="Address Line 2"]').value,
    address3: form.querySelector('textarea[placeholder="Address Line 3"]').value,
  };

  const confirmPassword = document.getElementById("confirmPassword").value;

  const errorMsg = document.getElementById("errorMsg");
  errorMsg.textContent = "";

  if (userData.password !== confirmPassword) {
    errorMsg.textContent = "Passwords do not match";
    return;
  }

  // ✅ SAVE DATA
  localStorage.setItem("userData", JSON.stringify(userData));

  alert("Account created successfully!");

  // 👉 redirect to login
  window.location.href = "login.html";
});

