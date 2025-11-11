import ApiService from "../services/apiService.js";

const carList = document.getElementById("carList");
const addCarBtn = document.getElementById("addCarBtn");
const modal = document.getElementById("carModal");
const closeModalBtn = document.getElementById("closeModalBtn");
const carForm = document.getElementById("carForm");
const modalTitle = document.getElementById("modalTitle");

let editCarId = "";
document.addEventListener("DOMContentLoaded", () => {
  loadCars();
});

async function loadCars() {
  try {
    const cars = await ApiService.get("/cars/");
    renderCars(cars);
  } catch (error) {
    console.error("Error fetching cars:", error);
    carList.innerHTML = `<p class="error-text">Failed to load cars.</p>`;
  }
}

function renderCars(cars = []) {
  if (!cars.length) {
    carList.innerHTML = `<p>No cars found. Add a new one!</p>`;
    return;
  }

  carList.innerHTML = cars
    .map(
      (car) => `
        <div class="car-card">
          <div class="car-info">
            <h3>${escapeHtml(car.company)}</h3>
            <p><strong>Model:</strong> ${escapeHtml(car.model)}</p>
            <p><strong>Kms Driven:</strong> ${escapeHtml(car.kms)}</p>
            <p><strong>Year:</strong> ${escapeHtml(car.year)}</p>
            <p><strong>Available:</strong> ${
              car.available ? "✅ Yes" : "❌ No"
            }</p>
          </div>
          <div class="car-actions">
            <button
              class="btn-edit"
              data-action="edit"
              data-id="${car.id}"
              data-name="${escapeAttr(car.company)}"
              data-model="${escapeAttr(car.model)}"
              data-kms="${escapeAttr(car.kms)}"
              data-year="${escapeAttr(car.year)}"
              data-color="${escapeAttr(car.color)}"
              data-available="${car.available}"
            >
              <i class="fa-solid fa-pen"></i>
            </button>
            <button
              class="btn-delete"
              data-action="delete"
              data-id="${car.id}"
            >
              <i class="fa-solid fa-trash"></i>
            </button>
          </div>
        </div>
      `
    )
    .join("");
}

addCarBtn.addEventListener("click", () => openModal());
closeModalBtn.addEventListener("click", () => closeModal());

function openModal(car = null) {
  modal.style.display = "flex";
  if (car) {
    modalTitle.textContent = "Edit Car";
    document.getElementById("company").value = car.company;
    document.getElementById("model").value = car.model;
    document.getElementById("kms").value = car.kms;
    document.getElementById("year").value = car.year;
    document.getElementById("color").value = car.color;
    [...document.getElementsByName("available")].forEach(
      (r) => (r.checked = r.value === car.available.toString())
    );
  } else {
    modalTitle.textContent = "Add New Car";
    carForm.reset();
  }
}

function closeModal() {
  modal.style.display = "none";
  editCarId = null;
}

carForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const availableValue = carForm.available.value === "true";



  const carData = {
    company: carForm.company.value,
    model: carForm.model.value,
    kms: parseInt(carForm.kms.value),
    year: parseInt(carForm.year.value),
    color: carForm.color.value,
    available: availableValue,
  };

  try {
    if (editCarId) {
      await ApiService.put(`/cars/${editCarId}`, carData);
    } else {
      await ApiService.post("/cars/", carData);
    }
    closeModal();
    loadCars();
  } catch (error) {
    console.error("Error saving car:", error);
  }
});

async function editCar(id, data) {
  editCarId = id;
  openModal(data);
}

async function deleteCar(id) {
  // if (!confirm("Are you sure you want to delete this car?")) return;
  try {
    await ApiService.delete(`/cars/${id}`);
    loadCars();
  } catch (error) {
    console.error("Error deleting car:", error);
  }
}

window.onclick = function (event) {
  if (event.target === modal) closeModal();
};

function escapeHtml(str = "") {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function escapeAttr(str = "") {
  return String(str).replaceAll('"', "&quot;");
}

carList.addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-action]");
  if (!btn) return;
  const action = btn.dataset.action;
  const id = btn.dataset.id;

  if (action === "edit") {
    // use data attributes to populate modal
    const data = {
      company: btn.dataset.name || "",
      model: btn.dataset.model || "",
      kms: btn.dataset.kms || "",
      year: btn.dataset.year || "",
      color: btn.dataset.color || "",
      available: btn.dataset.available || "",
    };
    console.log(id);
    editCar(id, data);
  } else if (action === "delete") {
    deleteCar(id);
  }
});
