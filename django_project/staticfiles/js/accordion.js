document.addEventListener('DOMContentLoaded', function () {
  initAccordion();
});

function initAccordion() {
  const accordionHeaders = document.querySelectorAll('.accordion-header');
  accordionHeaders.forEach(header => {
    header.addEventListener('click', function () {
      toggleAccordion(header);
    });
  });
}

function toggleAccordion(accordionHeader) {
  const accordionItem = accordionHeader.parentElement;
  const accordionCollapse = accordionItem.querySelector('.accordion-collapse');
  const accordionButton = accordionHeader.querySelector('.accordion-button');

  // Toggle the 'expanded' class
  accordionCollapse.classList.toggle('expanded');

  // Update aria-expanded attribute
  accordionButton.setAttribute('aria-expanded', accordionCollapse.classList.contains('expanded'));

  // Set the height for the accordion collapse
  if (accordionCollapse.classList.contains('expanded')) {
    // Add a small timeout to ensure the DOM is fully rendered before calculating the height
    setTimeout(() => {
      const accordionBody = accordionCollapse.firstElementChild;
      const expandedHeight = accordionBody.scrollHeight;
      accordionCollapse.style.height = expandedHeight + 'px';
    }, 20);
  } else {
    accordionCollapse.style.height = '0';
  }
}
