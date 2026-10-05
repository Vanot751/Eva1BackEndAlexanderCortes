document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector("#changelist-form");
    if (!form) return;

    form.addEventListener("submit", function(event) {
        const editedFields = form.querySelectorAll(
            ".field-nombre input, .field-descripcion input, " +
            ".field-precio input, .field-stock input"
        );

        const hasChanges = Array.from(editedFields).some((field) => {
            return field.value !== field.defaultValue;
        });

        if (hasChanges && !window.confirm(
            "¿Deseas guardar los cambios realizados en los productos seleccionados?"
        )) {
            event.preventDefault();
        }
    });
});
