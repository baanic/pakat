let draggedItem = null;

function allowDrop(e) {
  e.preventDefault();
}

function handleDrag(e) {
  draggedItem = e.target;
}

function handleDrop(e) {
  e.preventDefault();
  const target = e.target.closest(".task-section");
  if (!draggedItem || !target || draggedItem === e.target) return;
  target.appendChild(draggedItem);
  saveOrder();
}

function saveOrder() {
  const allItems = document.querySelectorAll(".task-item");
  const order = [...allItems].map(item => parseInt(item.dataset.id));
  fetch("/reorder-tasks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ order })
  });
}

function toggleTheme() {
  document.body.classList.toggle('dark-mode');
  const mode = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
  localStorage.setItem('theme', mode);
}

function applyFilters() {
  const incompleteOnly = document.getElementById("filterIncomplete").checked;
  const highPriorityOnly = document.getElementById("filterHighPriority").checked;
  const tag = document.getElementById("filterTag").value.trim();

  document.querySelectorAll(".task-item").forEach(item => {
    const completed = item.dataset.complete === "true";
    const priority = item.dataset.priority;
    const itemText = item.innerText;

    let show = true;
    if (incompleteOnly && completed) show = false;
    if (highPriorityOnly && priority !== "high") show = false;
    if (tag && !itemText.includes(tag)) show = false;

    item.style.display = show ? "block" : "none";
  });
}

function handleAddTask(e) {
  if (e.key === "Enter") {
    const input = e.target;
    const title = input.value.trim();
    if (!title) return;

    fetch("/add-task", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title })
    }).then(() => location.reload());
  }
}

function selectTask(taskEl) {
  const details = document.getElementById("task-details");
  const title = taskEl.querySelector("strong").innerText;
  const date = taskEl.querySelector("small").innerText;
  const id = taskEl.dataset.id;

  details.innerHTML = `
    <h4>${title}</h4>
    <p>${date}</p>
    <button onclick="deleteTask(${id})">🗑 حذف</button>
    <button onclick="markComplete(${id})">✔ انجام شد</button>
  `;
}

function deleteTask(id) {
  fetch("/delete-task", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id })
  }).then(() => location.reload());
}

function markComplete(id) {
  fetch("/complete-task", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id })
  }).then(() => location.reload());
}

function addNewList() {
  const name = prompt("نام لیست جدید را وارد کنید:");
  if (!name) return;
  alert("لیست‌ها در این نسخه صرفاً نمایشی هستند.");
}

window.onload = () => {
  const saved = localStorage.getItem('theme');
  if (saved === 'dark') document.body.classList.add('dark-mode');

  if ("Notification" in window && Notification.permission !== "granted") {
    Notification.requestPermission();
  }

  document.querySelectorAll(".task-item").forEach(task => {
    task.onclick = () => selectTask(task);
  });
};