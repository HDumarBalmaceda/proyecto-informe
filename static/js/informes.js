const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const form = document.getElementById('uploadForm');



// Click en el recuadro
dropZone.addEventListener('click', () => fileInput.click());

// Efecto visual al arrastrar
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () =>
    dropZone.classList.remove('dragover')
);

// Soltar archivo
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');

    const file = e.dataTransfer.files[0];

    if (file && file.name.toLowerCase().endsWith('.zip')) {
        fileInput.files = e.dataTransfer.files;

        dropZone.innerHTML = `
            <p class="text-gray-200 mb-2 font-semibold">📁 Archivo seleccionado:</p>
            <p class="text-cyan-400">${file.name}</p>
        `;
    } else {
        Swal.fire('⚠️ Archivo inválido', 'Solo se permiten archivos .zip exportados desde WhatsApp.', 'warning');
    }
});

// Envío del formulario
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const archivo = fileInput.files[0];
    if (!archivo) {
        Swal.fire('⚠️ Error', 'No se seleccionó ningún archivo ZIP.', 'warning');
        return;
    }

    // 🔥 NUEVO: obtener datos del formulario
    const fechaInicio = document.getElementById("fecha_inicio").value;
    const mesSeleccionado = document.getElementById("mesSeleccionado").value;

    if (!fechaInicio) {
        Swal.fire("⚠️ Falta la fecha", "Debes seleccionar una fecha válida.", "warning");
        return;
    }

    // Construir FormData
    const formData = new FormData();
    formData.append('archivo', archivo);
    formData.append('fecha_inicio', fechaInicio);        // <-- 🔥 NUEVO
    formData.append('mesSeleccionado', mesSeleccionado); // <-- 🔥 NUEVO

    // Alerta de carga
    Swal.fire({
        title: 'Procesando archivo...',
        text: 'Por favor espera mientras generamos el informe 📊',
        icon: 'info',
        allowOutsideClick: false,
        showConfirmButton: false,
        didOpen: () => Swal.showLoading()
    });

    try {
        const response = await fetch('/procesar', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        Swal.close();

        mostrarMensajeBackend(data.mensaje);

    } catch (error) {
        Swal.close();
        Swal.fire('❌ Error', 'No se pudo enviar el archivo al servidor.', 'error');
    }
});

/* === Función compartida con Jinja === */
function mostrarMensajeBackend(mensaje) {
    let icon = 'info';
    if (mensaje.startsWith('✅')) icon = 'success';
    else if (mensaje.startsWith('⚠️')) icon = 'warning';
    else if (mensaje.startsWith('❌')) icon = 'error';

    Swal.fire({
        title: 'Resultado del proceso',
        html: `<pre style="white-space: pre-wrap; text-align: left;">${mensaje.replace(/^[✅⚠️❌]\s*/, '')}</pre>`,
        icon: icon,
        confirmButtonColor: '#38bdf8',
        width: 600,
    });
}
