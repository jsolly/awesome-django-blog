function toggleAccordion(accordionHeader) {
  const accordionItem = accordionHeader.parentElement;
  const accordionCollapse = accordionItem.querySelector('.accordion-collapse');

  // Toggle the 'expanded' class
  accordionCollapse.classList.toggle('expanded');
}

function initAccordion() {
  const accordionButtons = document.querySelectorAll('.accordion-button');

  accordionButtons.forEach(button => {
    button.addEventListener('click', () => {
      toggleAccordion(button.parentElement);
    });
  });
}

// Initialize the accordion when the DOM content is loaded
document.addEventListener('DOMContentLoaded', initAccordion);
