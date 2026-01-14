// select all faq questions
const questions = document.querySelectorAll(".faq-question");

questions.forEach((question) => {
  question.addEventListener("click", () => {

    const currentItem = question.parentElement;

    // close all other items
    document.querySelectorAll(".faq-item").forEach((item) => {
      if (item !== currentItem) {
        item.classList.remove("active");
      }
    });

    // toggle current item
    currentItem.classList.toggle("active");
  });
});

const menuBtn = document.querySelector(".menu-btn");
const dropdown = document.querySelector(".dropdown");

menuBtn.addEventListener("click", () => {
  dropdown.classList.toggle("show");
});
