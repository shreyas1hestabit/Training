// ===============================
// PRODUCT DETAIL PAGE LOGIC
// ===============================

// 1️⃣ Get product ID from URL
const params = new URLSearchParams(window.location.search);
const productId = params.get("id");

// 2️⃣ Select HTML elements
const productImage = document.getElementById("productImage");
const productTitle = document.getElementById("productTitle");
const productBrand = document.getElementById("productBrand");
const productPrice = document.getElementById("productPrice");
const productRating = document.getElementById("productRating");
const productDescription = document.getElementById("productDescription");
const productCategory = document.getElementById("productCategory");
const productStock = document.getElementById("productStock");

// 3️⃣ Safety check (important)
if (!productId) {
  alert("Product not found");
  throw new Error("No product ID in URL");
}

// 4️⃣ Fetch product from DummyJSON
fetch(`https://dummyjson.com/products/${productId}`)
  .then((response) => {
    if (!response.ok) {
      throw new Error("Failed to fetch product");
    }
    return response.json();
  })
  .then((product) => {
    renderProduct(product);
  })
  .catch((error) => {
    console.error("Error loading product:", error);
  });

// 5️⃣ Render product data
function renderProduct(product) {
  productImage.src = product.thumbnail;
  productImage.alt = product.title;

  productTitle.textContent = product.title;
  productBrand.textContent = product.brand;
  productPrice.textContent = `₹${product.price}`;
  productRating.textContent = `⭐ ${product.rating}`;
  productDescription.textContent = product.description;
  productCategory.textContent = product.category;

  productStock.textContent =
    product.stock > 0 ? "In Stock" : "Out of Stock";
}
