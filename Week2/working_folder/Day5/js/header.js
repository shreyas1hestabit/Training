function updateHeaderCounts() {
  const wishlist = getData("wishlist");
  const cart = getData("cart");

  const wishlistCountEl = document.getElementById("wishlistCount");
  const cartCountEl = document.getElementById("cartCount");

  if (wishlistCountEl) {
    wishlistCountEl.textContent = wishlist.length;
  }

  if (cartCountEl) {
    const totalQty = cart.reduce((sum, item) => sum + item.qty, 0);
    cartCountEl.textContent = totalQty;
  }
}

// run on page load
updateHeaderCounts();
