const cartGrid = document.getElementById("cartGrid");
const totalPriceEl = document.getElementById("totalPrice");

// LOAD CART
function loadCart() {
  let cart = getData("cart");
  cartGrid.innerHTML = "";
  let total = 0;

  if (cart.length === 0) {
    cartGrid.innerHTML = "<p>Your cart is empty</p>";
    totalPriceEl.textContent = "";
    return;
  }

  cart.forEach(product => {
    total += product.price * product.qty;

    const card = document.createElement("div");
    card.className = "product-card";

    card.innerHTML = `
      <img src="${product.thumbnail}" alt="${product.title}">
      <h3>${product.title}</h3>
      <p>$ ${product.price}</p>

      <div class="qty-controls">
        <button class="decrease">-</button>
        <span>${product.qty}</span>
        <button class="increase">+</button>
      </div>

      <button class="remove-btn">Remove</button>
    `;

    // QTY DECREASE
    card.querySelector(".decrease").addEventListener("click", () => {
      updateQty(product.id, -1);
    });

    // QTY INCREASE
    card.querySelector(".increase").addEventListener("click", () => {
      updateQty(product.id, 1);
    });

    // REMOVE
    card.querySelector(".remove-btn").addEventListener("click", () => {
      removeFromCart(product.id);
    });

    cartGrid.appendChild(card);
  });

  totalPriceEl.textContent = `Total: $ ${total}`;
}

// UPDATE QTY
function updateQty(id, change) {
  let cart = getData("cart");

  cart = cart.map(item => {
    if (item.id === id) {
      item.qty += change;
      if (item.qty < 1) item.qty = 1;
    }
    return item;
  });

  saveData("cart", cart);
  loadCart();
}

// REMOVE ITEM
function removeFromCart(id) {
  let cart = getData("cart");
  cart = cart.filter(item => item.id !== id);
  saveData("cart", cart);
  loadCart();
}

// INIT
loadCart();
