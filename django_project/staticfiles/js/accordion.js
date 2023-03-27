document.addEventListener('DOMContentLoaded', initAccordion);

function initAccordion() {
  const accordionHeaders = document.querySelectorAll('.accordion-header');
  accordionHeaders.forEach(header => {
    header.addEventListener('click', () => toggleAccordion(header));
  });
}

function toggleAccordion(accordionHeader) {
  const accordionItem = accordionHeader.parentElement;
  const accordionCollapse = accordionItem.querySelector('.accordion-collapse');
  const accordionButton = accordionHeader.querySelector('.accordion-button');
  const isExpanded = accordionCollapse.classList.toggle('expanded');

  // Update aria-expanded attribute
  accordionButton.setAttribute('aria-expanded', isExpanded);

  // Set the height for the accordion collapse
  accordionCollapse.style.height = isExpanded ? `${accordionCollapse.firstElementChild.scrollHeight}px` : '0';
}
