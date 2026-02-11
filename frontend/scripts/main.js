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
    carList.innerHTML = `
      <div class="loading">
        <i class="fa-solid fa-spinner fa-spin"></i> Loading vehicles...
      </div>
    `;
    const cars = await ApiService.get("/cars/");
    renderCars(cars);
  } catch (error) {
    console.error("Error fetching cars:", error);
    carList.innerHTML = `
      <div style="text-align: center; padding: 2rem; color: var(--color-danger);">
        <i class="fa-solid fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 1rem;"></i>
        <p>Failed to load vehicles. Please try again.</p>
      </div>
    `;
  }
}

function renderCars(cars = []) {
  if (!cars.length) {
    carList.innerHTML = `
      <div style="text-align: center; padding: 3rem; color: var(--color-muted-dark);">
        <i class="fa-solid fa-car" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
        <p style="font-size: 1.2rem;">No vehicles found. Add your first vehicle!</p>
      </div>
    `;
    return;
  }

  carList.innerHTML = cars
    .map(
      (car) => `
        <div class="car-card">
          <div class="car-info">
            <h3><i class="fa-solid fa-car"></i> ${escapeHtml(car.company)} ${escapeHtml(car.model)}</h3>
            <p><i class="fa-solid fa-palette"></i> <strong>Color:</strong> ${escapeHtml(car.color)}</p>
            <p><i class="fa-solid fa-road"></i> <strong>Mileage:</strong> ${escapeHtml(car.kms).toLocaleString()} km</p>
            <p><i class="fa-solid fa-calendar"></i> <strong>Year:</strong> ${escapeHtml(car.year)}</p>
            <span class="status ${car.available ? 'available' : 'unavailable'}">
              <i class="fa-solid fa-${car.available ? 'check-circle' : 'times-circle'}"></i>
              ${car.available ? 'Available' : 'Unavailable'}
            </span>
          </div>
          <div class="car-actions">
            <button
              title="Edit Vehicle"
              data-action="edit"
              data-id="${car.id}"
              data-name="${escapeAttr(car.company)}"
              data-model="${escapeAttr(car.model)}"
              data-kms="${escapeAttr(car.kms)}"
              data-year="${escapeAttr(car.year)}"
              data-color="${escapeAttr(car.color)}"
              data-available="${car.available}"
            >
              <i class="fa-solid fa-edit"></i>
            </button>
            <button
              title="Delete Vehicle"
              class="delete"
              data-action="delete"
              data-id="${car.id}"
            >
              <i class="fa-solid fa-trash-alt"></i>
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
    modalTitle.innerHTML = '<i class="fa-solid fa-edit"></i> Edit Vehicle';
    document.getElementById("company").value = car.company;
    document.getElementById("model").value = car.model;
    document.getElementById("kms").value = car.kms;
    document.getElementById("year").value = car.year;
    document.getElementById("color").value = car.color;
    [...document.getElementsByName("available")].forEach(
      (r) => (r.checked = r.value === car.available.toString())
    );
  } else {
    modalTitle.innerHTML = '<i class="fa-solid fa-plus-circle"></i> Add New Vehicle';
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
