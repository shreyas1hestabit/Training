// ---------------- FAQ ACCORDION SCRIPT ----------------

// Sabhi FAQ questions ko select kar rahe hain
const questions = document.querySelectorAll(".faq-question");

// Har question pe click event lagaya
questions.forEach((question) => {

  // Jab user kisi question pe click kare
  question.addEventListener("click", () => {

    // Jis FAQ pe click hua uska parent (.faq-item) le liya
    const currentItem = question.parentElement;

    // Pehle se open saare FAQ close kar dena
    document.querySelectorAll(".faq-item").forEach((item) => {

      // Agar item current wale se alag hai
      if (item !== currentItem) {

        // Uska active class hata do (close ho jayega)
        item.classList.remove("active");
      }
    });

    // Ab current FAQ ko open / close karna
    // Agar open hai toh close, band hai toh open
    currentItem.classList.toggle("active");
  });
});


// ---------------- DROPDOWN MENU SCRIPT ----------------

// Menu button ko select kiya
const menuBtn = document.querySelector(".menu-btn");

// Dropdown menu ko select kiya
const dropdown = document.querySelector(".dropdown");

// Menu button pe click event lagaya
menuBtn.addEventListener("click", () => {

  // Dropdown ka show class on / off kar rahe hain
  dropdown.classList.toggle("show");
});
