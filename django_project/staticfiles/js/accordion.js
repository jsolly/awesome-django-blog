
function toggleAccordion(accordionHeader) {
    const accordionItem = accordionHeader.parentElement;
    const accordionCollapse = accordionItem.querySelector('.accordion-collapse');
  
    const isOpen = accordionCollapse.style.display === 'block';
  
    if (isOpen) {
      accordionCollapse.style.display = 'none';
    } else {
      accordionCollapse.style.display = 'block';
    }
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