const hamburgerBtn = document.querySelector(".menu-hamburger-btn");
const hamburgerMenu = document.querySelector(".menu-hamburger-list");

hamburgerBtn.addEventListener("click", () => {
  hamburgerMenu.classList.toggle("active");
});

/* close menu when clicking outside */
document.addEventListener("click", (e) => {
  if (
    !hamburgerMenu.contains(e.target) &&
    !hamburgerBtn.contains(e.target)
  ) {
    hamburgerMenu.classList.remove("active");
  }
});

const productsContainer = document.querySelector(".products");

async function loadHomeProducts() {
  try {
    const response = await fetch("https://dummyjson.com/products");
    const data = await response.json();

    const products = data.products;

    // 👉 unique categories nikalna
    const categoryMap = {};

    products.forEach(product => {
      if (!categoryMap[product.category]) {
        categoryMap[product.category] = product;
      }
    });

    // 👉 sirf 5 categories/products lo
    const selectedProducts = Object.values(categoryMap).slice(0, 5);

    // 👉 cards banana
    productsContainer.innerHTML="";
    selectedProducts.forEach(product => {
      const card = document.createElement("div");
      card.classList.add("product-card");

      card.innerHTML = `
        <img src="${product.thumbnail}" alt="${product.title}">
        <h3>${product.title}</h3>
        <p>$ ${product.price}</p>
      `;
      card.addEventListener("click",() => {
        window.location.href='product.html?id=${product.id}';});

      productsContainer.appendChild(card);
    });

  } catch (error) {
    console.error("Error fetching products:", error);
  }
}

// page load pe call
loadHomeProducts();

