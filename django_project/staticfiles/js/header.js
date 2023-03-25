document.addEventListener('DOMContentLoaded', function () {
  var hamburger = document.querySelector('.hamburger');

  hamburger.addEventListener('click', function () {
    console.log('click');
    toggleMenu();
  });

  var dropdownToggles = document.querySelectorAll('.dropdown-toggle');

  dropdownToggles.forEach(function (toggle) {
    toggle.addEventListener('click', function (event) {
      event.preventDefault();
      var dropdownMenu = toggle.nextElementSibling;
      dropdownMenu.classList.toggle('show');
    });
  });
});

function toggleMenu() {
  var menu = document.querySelector('.navbar-menu');
  menu.classList.toggle('show-menu');
  console.log(menu.classList);
}
