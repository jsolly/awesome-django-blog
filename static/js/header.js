document.addEventListener("DOMContentLoaded", () => {
  const hamburger = document.querySelector(".hamburger");

  hamburger.addEventListener("click", () => {
    console.log("click");
    toggleMenu();
  });

  const dropdownToggles = document.querySelectorAll(".dropdown-toggle");

  dropdownToggles.forEach((toggle) => {
    toggle.addEventListener("click", (event) => {
      event.preventDefault();
      const dropdownMenu = toggle.nextElementSibling;
      dropdownMenu.classList.toggle("show");
    });
  });
});

function toggleMenu() {
  const menu = document.querySelector(".navbar-menu");
  menu.classList.toggle("show-menu");
  console.log(menu.classList);
}
