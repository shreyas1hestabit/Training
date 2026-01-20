const productsGrid = document.getElementById("productsGrid");
const searchInput = document.getElementById("searchInput");
const categoryFilter = document.getElementById("categoryFilter");
const priceSort = document.getElementById("priceSort");
const priceRange = document.getElementById("priceRange");
const priceValue = document.getElementById("priceValue");

let allProducts = [];
let filteredProducts = [];

// ---------------- FETCH PRODUCTS ----------------
async function fetchProducts() {
  try {
    const res = await fetch("https://dummyjson.com/products?limit=100");
    const data = await res.json();

    allProducts = data.products;
    filteredProducts = [...allProducts];

    populateCategories(allProducts);
    renderProducts(filteredProducts);
  } catch (err) {
    console.error("Error loading products", err);
  }
}

// ---------------- CATEGORIES ----------------
function populateCategories(products) {
  const categories = [...new Set(products.map(p => p.category))];

  categories.forEach(cat => {
    const option = document.createElement("option");
    option.value = cat;
    option.textContent = cat.toUpperCase();
    categoryFilter.appendChild(option);
  });
}

// ---------------- RENDER PRODUCTS ----------------
function renderProducts(products) {
  productsGrid.innerHTML = "";

  products.forEach(product => {
    const card = document.createElement("div");
    card.className = "product-card";

    card.innerHTML = `
      <div class="product-image">
        <img src="${product.thumbnail}" alt="${product.title}">
        <button class="wishlist-btn" title="Add to wishlist">
          <img src="../assets/heart.svg">
        </button>
      </div>

      <h3>${product.title}</h3>
      <p>$ ${product.price}</p>

      <button class="add-to-cart-btn">Add to Cart</button>
    `;

    //  WISHLIST
    card.querySelector(".wishlist-btn").addEventListener("click", () => {
      let wishlist = getData("wishlist");

      if (!wishlist.find(item => item.id === product.id)) {
        wishlist.push(product);
        saveData("wishlist", wishlist);
        alert("Added to wishlist ");
      }
    });

    // ADD TO CART
    card.querySelector(".add-to-cart-btn").addEventListener("click", () => {
      let cart = getData("cart");
      const existing = cart.find(item => item.id === product.id);

      if (existing) {
        existing.qty += 1;
      } else {
        cart.push({ ...product, qty: 1 });
      }

      saveData("cart", cart);
      alert("Added to cart ");
      updateHeaderCounts();
    });

    productsGrid.appendChild(card);
  });
}

// ---------------- FILTERS ----------------
categoryFilter.addEventListener("change", () => {
  const value = categoryFilter.value;

  filteredProducts =
    value === "all"
      ? [...allProducts]
      : allProducts.filter(p => p.category === value);

  applySort();
});

priceSort.addEventListener("change", applySort);

function applySort() {
  let sorted = [...filteredProducts];

  if (priceSort.value === "low-high") {
    sorted.sort((a, b) => a.price - b.price);
  } else if (priceSort.value === "high-low") {
    sorted.sort((a, b) => b.price - a.price);
  }

  renderProducts(sorted);
}

// ---------------- PRICE RANGE ----------------
priceRange.addEventListener("input", () => {
  const maxPrice = priceRange.value;
  priceValue.textContent = `Up to $${maxPrice}`;

  filteredProducts = allProducts.filter(
    product => product.price <= maxPrice
  );

  applySort();
});

// ---------------- SEARCH ----------------
searchInput.addEventListener("input", e => {
  const value = e.target.value.toLowerCase();

  filteredProducts = allProducts.filter(p =>
    p.title.toLowerCase().includes(value)
  );

  applySort();
});

// ---------------- INIT ----------------
fetchProducts();
