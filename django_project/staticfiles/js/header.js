document.addEventListener('DOMContentLoaded', function () {
    var hamburger = document.querySelector('.hamburger');
  
    hamburger.addEventListener('click', function () {
      console.log('click');
      toggleMenu();
    });
  });
  
  function toggleMenu() {
    var menu = document.querySelector('.navbar-menu');
    menu.classList.toggle('show-menu');
    console.log(menu.classList); // Add this line
  }
  