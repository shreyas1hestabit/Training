const wishlistGrid = document.getElementById("wishlistGrid");

// LOAD WISHLIST
function loadWishlist() {
   wishlist = getData("wishlist");
  wishlistGrid.innerHTML = "";

  if (wishlist.length === 0) {
    wishlistGrid.innerHTML = "<p>No items in wishlist</p>";
    return;
  }

  wishlist.forEach(product => {
    const card = document.createElement("div");
    card.className = "product-card";

    card.innerHTML = `
      <img src="${product.thumbnail}" alt="${product.title}">
      <h3>${product.title}</h3>
      <p>$ ${product.price}</p>

      <div style="display:flex; gap:10px;">
        <button class="add-cart-btn">Move to Cart</button>
        <button class="remove-btn">Remove</button>
      </div>
    `;

    // REMOVE FROM WISHLIST
    card.querySelector(".remove-btn").addEventListener("click", () => {
      removeFromWishlist(product.id);
    });

    // MOVE TO CART
    card.querySelector(".add-cart-btn").addEventListener("click", () => {
      moveToCart(product);
    });

    wishlistGrid.appendChild(card);
  });
}

// REMOVE
function removeFromWishlist(id) {
  let wishlist = getData("wishlist");
  wishlist = wishlist.filter(item => item.id !== id);
  saveData("wishlist", wishlist);
  loadWishlist();
}

// MOVE TO CART
function moveToCart(product) {
  let cart = getData("cart");

  const existing = cart.find(item => item.id === product.id);
  if (existing) {
    existing.qty += 1;
  } else {
    cart.push({ ...product, qty: 1 });
  }

  saveData("cart", cart);
  updateHeaderCounts();
  removeFromWishlist(product.id);
}

// INIT
loadWishlist();
