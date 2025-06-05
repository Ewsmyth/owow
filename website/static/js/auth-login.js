document.addEventListener("DOMContentLoaded", function () {
    const togglePassword = document.getElementById("togglePassword");
    const passwordInput = document.getElementById("password");

    togglePassword.addEventListener("click", function () {
        const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
        passwordInput.setAttribute("type", type);
        togglePassword.textContent = type === "password" ? "👁️" : "🙈";
    });

    const inputs = document.querySelectorAll(".input-group input");

    inputs.forEach(input => {
        input.addEventListener("focus", () => {
            input.parentNode.classList.add("active");
        });

        input.addEventListener("blur", () => {
            if (input.value === "") {
                input.parentNode.classList.remove("active");
            }
        });
    });
});
