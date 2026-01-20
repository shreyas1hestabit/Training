fetch("https://dummyjson.com/products")
  .then(res => res.json())
  .then(data => {
    const products = data.products;
    const productsGrid = document.querySelector(".products-grid");

    const uniqueCategoryProducts = {};
    const finalProducts = [];

    for (let product of products) {
      if (!uniqueCategoryProducts[product.category]) {
        uniqueCategoryProducts[product.category] = true;
        finalProducts.push(product);
      }
      if (finalProducts.length === 6) break;
    }

    renderHomeProducts(finalProducts, productsGrid);
  })
  .catch(err => {
    console.error("Error fetching products:", err);
  });

/* -----------------------------
   HOME PAGE RENDER FUNCTION
------------------------------ */
function renderHomeProducts(products, container) {
  container.innerHTML = "";

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
    `;

    container.appendChild(card);
  });
}
