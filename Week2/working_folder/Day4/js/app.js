const form = document.getElementById("todo-form");
const input = document.getElementById("todo-input");
const list = document.getElementById("todo-list");

let todos = getTodos();
renderTodos();

// Add Todo
form.addEventListener("submit", function (e) {
  e.preventDefault();

  try {
    const todoText = input.value.trim();
    if (!todoText) return;

    const todo = {
      id: Date.now(),
      text: todoText
    };

    todos.push(todo);
    saveTodos(todos);
    renderTodos();
    input.value = "";
  } catch (error) {
    console.error("Add Todo Error:", error);
  }
});

// Render Todos
function renderTodos() {
  list.innerHTML = "";

  todos.forEach(todo => {
    const li = document.createElement("li");
    li.textContent = todo.text;

    // Edit Button
    const editBtn = document.createElement("button");
    editBtn.textContent = "Edit";
    editBtn.onclick = () => editTodo(todo.id);

    // Delete Button
    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "Delete";
    deleteBtn.onclick = () => deleteTodo(todo.id);

    li.append(editBtn, deleteBtn);
    list.appendChild(li);
  });
}

// Edit Todo
function editTodo(id) {
  try {
    const newText = prompt("Edit todo:");
    if (!newText) return;

    todos = todos.map(todo =>
      todo.id === id ? { ...todo, text: newText } : todo
    );

    saveTodos(todos);
    renderTodos();
  } catch (error) {
    console.error("Edit Todo Error:", error);
  }
}

// Delete Todo
function deleteTodo(id) {
  try {
    todos = todos.filter(todo => todo.id !== id);
    saveTodos(todos);
    renderTodos();
  } catch (error) {
    console.error("Delete Todo Error:", error);
  }
}

// ---------------- DROPDOWN MENU SCRIPT ----------------

// Menu button ko select kiya
const menuBtn = document.querySelector(".menu-btn");

// Dropdown menu ko select kiya
const dropdown = document.querySelector(".dropdown");

// Menu button pe click event lagaya
menuBtn.addEventListener("click", () => {

  // Dropdown ka show class on / off kar rahe hain
  dropdown.classList.toggle("show");
});
