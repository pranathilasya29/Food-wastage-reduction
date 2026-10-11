
document.addEventListener("DOMContentLoaded", function () {
    const buttons = document.querySelectorAll("[data-confirm]");

    buttons.forEach(function (button) {
        button.addEventListener("click", function (event) {
            const message = button.dataset.confirm;

            if (message && !window.confirm(message)) {
                event.preventDefault();
            }
        });
    });
});
