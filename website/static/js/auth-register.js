document.addEventListener("DOMContentLoaded", function () {
  const toggleIcons = document.querySelectorAll(".toggle-password");
  const inputs = document.querySelectorAll(".input-group input");

  toggleIcons.forEach(icon => {
    icon.addEventListener("click", function () {
      const input = icon.previousElementSibling;
      const isPassword = input.getAttribute("type") === "password";
      input.setAttribute("type", isPassword ? "text" : "password");
      icon.textContent = isPassword ? "🙈" : "👁️";
    });
  });

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
