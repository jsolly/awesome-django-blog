// accordion.js

function toggleAccordion(accordionHeader) {
    const accordionItem = accordionHeader.parentElement;
    const accordionCollapse = accordionItem.querySelector('.accordion-collapse');
  
    // Toggle the 'expanded' class
    accordionCollapse.classList.toggle('expanded');
  }
  
  function initAccordion() {
    const accordionHeaders = document.querySelectorAll('.accordion-header');
  
    accordionHeaders.forEach(header => {
      header.addEventListener('click', () => {
        toggleAccordion(header);
      });
    });
  }
  
  // Initialize the accordion when the window has finished loading
  window.addEventListener('load', initAccordion);
  