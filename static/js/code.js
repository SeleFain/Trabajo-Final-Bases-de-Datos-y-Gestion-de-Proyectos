document.addEventListener("DOMContentLoaded", () => {
    const formulario = document.getElementById("formulario-cliente");
    const tablaClientes = document.getElementById("tabla-clientes");

    // 1. FUNCIÓN PARA OBTENER Y MOSTRAR CLIENTES
    const cargarClientes = async () => {
        try {
            const respuesta = await fetch("/api/clientes");
            const clientes = await respuesta.json();
            
            // Limpiamos la tabla
            tablaClientes.innerHTML = "";

            // Insertamos cada cliente en la tabla
            clientes.forEach(cliente => {
                const fila = document.createElement("tr");
                fila.innerHTML = `
                    <td>${cliente.id}</td>
                    <td>${cliente.nombre}</td>
                    <td>${cliente.email}</td>
                    <td>${cliente.telefono || 'N/A'}</td>
                `;
                tablaClientes.appendChild(fila);
            });
        } catch (error) {
            console.error("Error al cargar clientes:", error);
        }
    };

    // 2. EVENTO PARA ENVIAR EL FORMULARIO (POST)
    formulario.addEventListener("submit", async (e) => {
        e.preventDefault(); // Evita que la página se recargue

        const datos = {
            nombre: document.getElementById("nombre").value,
            email: document.getElementById("email").value,
            telefono: document.getElementById("telefono").value
        };

        try {
            const respuesta = await fetch("/api/clientes", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(datos)
            });

            const resultado = await respuesta.json();

            if (respuesta.ok) {
                alert(resultado.mensaje);
                formulario.reset(); // Limpia los inputs del formulario
                cargarClientes();   // Recarga la lista reflejando el nuevo usuario
            } else {
                alert("Error: " + resultado.error);
            }
        } catch (error) {
            console.error("Error al registrar cliente:", error);
        }
    });

    // Cargar los clientes existentes inmediatamente al abrir la página
    cargarClientes();
});
