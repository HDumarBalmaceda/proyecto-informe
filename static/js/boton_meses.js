// Abrir/cerrar menú
const button = document.getElementById("dropdownButton");
const menu = document.getElementById("dropdownMenu");
const selectedText = document.getElementById("selectedMonthText");
const inputHidden = document.getElementById("mesSeleccionado");

button.addEventListener("click", () => {
    menu.classList.toggle("hidden");
});

// Seleccionar un mes
document.querySelectorAll(".month-option").forEach(option => {
    option.addEventListener("click", () => {
        const month = option.getAttribute("data-month");

        selectedText.textContent = option.textContent;
        inputHidden.value = month;

        menu.classList.add("hidden");
    });
});

// Cerrar si se hace clic afuera
window.addEventListener("click", (e) => {
    if (!button.contains(e.target) && !menu.contains(e.target)) {
        menu.classList.add("hidden");
    }
});

// --- Botón Consolidar mes  ---
const btnConsolidar = document.getElementById("btnConsolidar");

btnConsolidar.addEventListener("click", async () => {
    const mesSeleccionado = inputHidden.value; // ya lo tienes del dropdown

    if (!mesSeleccionado) {
        Swal.fire("⚠️ Falta el mes", "Debes seleccionar un mes para consolidar.", "warning");
        return;
    }

    const formData = new FormData();
    formData.append("mesSeleccionado", mesSeleccionado);

    // Alerta de carga
    Swal.fire({
        title: 'Consolidando informes...',
        text: `Estamos generando el consolidado de ${mesSeleccionado} 📊`,
        icon: 'info',
        allowOutsideClick: false,
        showConfirmButton: false,
        didOpen: () => Swal.showLoading()
    });

    try {
        const response = await fetch("/consolidar", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        Swal.close();

        // Reutilizamos tu función de mostrar mensajes
        mostrarMensajeBackend(data.mensaje);

    } catch (error) {
        Swal.close();
        Swal.fire("❌ Error", "No se pudo consolidar los informes.", "error");
    }
});

// --- Botón Consolidar año ---
const btnConsolidarAnual = document.getElementById("btnConsolidarAnual");

btnConsolidarAnual.addEventListener("click", async () => {
    // Alerta de carga
    Swal.fire({
        title: 'Generando informe anual...',
        text: 'Estamos consolidando todos los informes del año 📊',
        icon: 'info',
        allowOutsideClick: false,
        showConfirmButton: false,
        didOpen: () => Swal.showLoading()
    });

    try {
        const response = await fetch("/consolidar_anual", {
            method: "POST"
        });

        const data = await response.json();
        Swal.close();

        // Reutilizamos tu función de mostrar mensajes
        mostrarMensajeBackend(data.mensaje);

    } catch (error) {
        Swal.close();
        Swal.fire("❌ Error", "No se pudo consolidar los informes del año.", "error");
    }
});

