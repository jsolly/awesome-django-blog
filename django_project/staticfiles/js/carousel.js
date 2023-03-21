document.addEventListener('DOMContentLoaded', function() {
    let currentCarouselIndex = 0;
    const carouselItems = document.querySelectorAll('.carousel-item');
  
    function changeCarouselItem(step) {
      carouselItems[currentCarouselIndex].classList.remove('active');
      currentCarouselIndex = (currentCarouselIndex + step + carouselItems.length) % carouselItems.length;
      carouselItems[currentCarouselIndex].classList.add('active');
    }
  
    const prevControl = document.querySelector('.carousel-control-prev');
    const nextControl = document.querySelector('.carousel-control-next');
  
    prevControl.addEventListener('click', function() {
      changeCarouselItem(-1);
    });
  
    nextControl.addEventListener('click', function() {
      changeCarouselItem(1);
    });
  });
  