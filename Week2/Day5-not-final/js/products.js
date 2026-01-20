// products.js

document.addEventListener("DOMContentLoaded", () => {

  /* -----------------------------
     READ CATEGORY FROM URL
  ------------------------------ */
  const params = new URLSearchParams(window.location.search);
  const category = params.get("category"); // e.g. smartphones

  /* -----------------------------
     SELECT DOM ELEMENTS
  ------------------------------ */
  const headingEl = document.querySelector(".products-header h1");
  const breadcrumbEl = document.querySelector(".breadcrumb");
  const productsGrid = document.querySelector(".products-grid");

  /* -----------------------------
     FORMAT CATEGORY NAME
  ------------------------------ */
  function formatCategory(text) {
    if (!text) return "";
    return text
      .split("-")
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  }

  /* -----------------------------
     UPDATE HEADING & BREADCRUMB
  ------------------------------ */
  if (category) {
    const readableCategory = formatCategory(category);
    headingEl.textContent = readableCategory;
    breadcrumbEl.textContent = `Home / Products / ${readableCategory}`;
  } else {
    headingEl.textContent = "All Products";
    breadcrumbEl.textContent = "Home / Products";
  }

  console.log("Selected category:", category);

  /* -----------------------------
     FETCH PRODUCTS (DummyJSON)
  ------------------------------ */
  fetch("https://dummyjson.com/products")
    .then(res => res.json())
    .then(data => {
      let products = data.products;

      // Filter by category (if present)
      if (category) {
        products = products.filter(product =>
          product.category.toLowerCase() === category.toLowerCase()
        );
      }

      renderProducts(products);
    })
    .catch(err => {
      console.error("Error fetching products:", err);
      productsGrid.innerHTML = "<p>Failed to load products</p>";
    });

  /* -----------------------------
     RENDER PRODUCTS
  ------------------------------ */
  function renderProducts(products) {
    productsGrid.innerHTML = "";

    if (!products || products.length === 0) {
      productsGrid.innerHTML = "<p>No products found</p>";
      return;
    }

    products.forEach(product => {
      const card = document.createElement("article");
      card.className = "product-card";

      card.innerHTML = `
        <div class="product-image">
          <img src="${product.thumbnail}" alt="${product.title}">
        </div>

        <div class="product-info">
          <h3 class="product-title">${product.title}</h3>
          <p class="product-price">₹${product.price}</p>
          <p class="product-rating">⭐ ${product.rating}</p>
        </div>

        <div class="product-actions">
          <button class="add-to-cart">Add to Cart</button>
          <button class="wishlist-icon">
            <img src="assets/heart.svg" alt="wishlist">
          </button>
        </div>
      `;

      productsGrid.appendChild(card);
    });
  }

});
