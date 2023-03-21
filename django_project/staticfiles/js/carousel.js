let currentCarouselIndex = 0;
const carouselItems = document.querySelectorAll('.carousel-item');

function changeCarouselItem(step) {
  carouselItems[currentCarouselIndex].classList.remove('active');
  currentCarouselIndex = (currentCarouselIndex + step + carouselItems.length) % carouselItems.length;
  carouselItems[currentCarouselIndex].classList.add('active');
}