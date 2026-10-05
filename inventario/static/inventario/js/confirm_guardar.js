document.addEventListener("DOMContentLoaded", function() {
    // Buscar todos los inputs editables en la lista del admin
    const inputs = document.querySelectorAll("#changelist-form .field-nombre input, #changelist-form .field-descripcion input, #changelist-form .field-precio input, #changelist-form .field-stock input");
    
    inputs.forEach(input => {
        // Guardamos el valor original cuando la página carga
        input.dataset.oldValue = input.value;

        input.addEventListener("change", function(e) {
            const original = input.dataset.oldValue;
            const current = input.value;
            
            // Si el valor no cambió realmente, no hacemos nada
            if (original === current) return;

            // Extraemos el nombre del campo para mostrar un mensaje claro
            let fieldName = "valor";
            if (input.name.includes("nombre")) fieldName = "nombre";
            if (input.name.includes("descripcion")) fieldName = "descripción";
            if (input.name.includes("precio")) fieldName = "precio";
            if (input.name.includes("stock")) fieldName = "stock";

            const confirmMsg = `¿Estás seguro de que deseas cambiar el ${fieldName}?\nDe: "${original}"\nA: "${current}"`;
            
            if (!confirm(confirmMsg)) {
                // El usuario canceló la modificación, restauramos el valor
                input.value = original;
            } else {
                // Confirmado, actualizamos el oldValue para futuras modificaciones
                input.dataset.oldValue = current;
            }
        });
    });
});

