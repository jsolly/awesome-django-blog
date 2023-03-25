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

  // Calculate the height of the accordion body
  const accordionBody = accordionCollapse.firstElementChild;
  const expandedHeight = accordionBody.scrollHeight;

  // Toggle the 'expanded' class
  accordionCollapse.classList.toggle('expanded');

  // Update aria-expanded attribute
  accordionButton.setAttribute('aria-expanded', accordionCollapse.classList.contains('expanded'));

  // Set the height for the accordion collapse
  if (accordionCollapse.classList.contains('expanded')) {
    accordionCollapse.style.height = expandedHeight + 'px';
  } else {
    accordionCollapse.style.height = '0';
  }
}