// Wait for the DOM to finish loading before executing the code
document.addEventListener('DOMContentLoaded', () => {
  // Initialize the current index to 0 and get references to the carousel items and indicators
  let currentCarouselIndex = 0;
  const carouselItems = document.querySelectorAll('.carousel-item');
  const indicators = document.querySelectorAll('.carousel-indicators li');

  // Update the indicators to reflect the current index
  const updateIndicators = () => {
    indicators.forEach((indicator, index) => {
      indicator.classList.toggle('active', index === currentCarouselIndex);
    });
  };

  // Change the active carousel item
  const changeCarouselItem = (value) => {
    carouselItems[currentCarouselIndex].classList.remove('active');

    if (typeof value === 'number') {
      currentCarouselIndex = value;
    } else {
      currentCarouselIndex = (currentCarouselIndex + value + carouselItems.length) % carouselItems.length;
    }

    carouselItems[currentCarouselIndex].classList.add('active');
    updateIndicators();
  };

  // Add click event listeners to the previous and next carousel controls
  document.querySelector('.carousel-control-prev').addEventListener('click', () => {
    changeCarouselItem(-1);
  });

  document.querySelector('.carousel-control-next').addEventListener('click', () => {
    changeCarouselItem(1);
  });

  // Add click event listeners to the carousel indicators
  document.querySelectorAll('[data-carousel-index]').forEach((item) => {
    item.addEventListener('click', () => {
      const index = parseInt(item.dataset.carouselIndex);
      changeCarouselItem(index);
    });
  });
});
