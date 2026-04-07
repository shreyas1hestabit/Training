document.addEventListener("DOMContentLoaded", async () => {
  const categoriesList = document.querySelector(".categories-list");

  console.log("Categories container:", categoriesList);

  if (!categoriesList) {
    console.error("❌ .categories-list NOT FOUND");
    return;
  }

  try {
    const res = await fetch("https://dummyjson.com/products/categories");
    const categories = await res.json();

    console.log("Fetched categories:", categories);

    categoriesList.innerHTML = "";

    categories.forEach(cat => {
      const div = document.createElement("div");
      div.className = "category-item";
      div.textContent = formatCategory(cat);

      div.addEventListener("click", () => {
        window.location.href = `products.html?category=${cat}`;
      });

      categoriesList.appendChild(div);
    });
  } catch (err) {
    console.error("❌ API error", err);
  }
});

function formatCategory(text) {
  return text
    .split("-")
    .map(w => w[0].toUpperCase() + w.slice(1))
    .join(" ");
}
