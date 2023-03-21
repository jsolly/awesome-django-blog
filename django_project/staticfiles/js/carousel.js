document.addEventListener('DOMContentLoaded', function() {
    let currentCarouselIndex = 0;
    const carouselItems = document.querySelectorAll('.carousel-item');
    const indicators = document.querySelectorAll('.carousel-indicators li');
  
    function updateIndicators() {
      indicators.forEach(function(indicator, index) {
        if (index === currentCarouselIndex) {
          indicator.classList.add('active');
        } else {
          indicator.classList.remove('active');
        }
      });
    }
  
    function changeCarouselItem(step) {
      carouselItems[currentCarouselIndex].classList.remove('active');
      currentCarouselIndex = (currentCarouselIndex + step + carouselItems.length) % carouselItems.length;
      carouselItems[currentCarouselIndex].classList.add('active');
      updateIndicators();
    }
  
    function changeCarouselItemTo(index) {
      if (index === currentCarouselIndex) return;
      carouselItems[currentCarouselIndex].classList.remove('active');
      currentCarouselIndex = index;
      carouselItems[currentCarouselIndex].classList.add('active');
      updateIndicators();
    }
  
    window.changeCarouselItemTo = changeCarouselItemTo;
  
    const prevControl = document.querySelector('.carousel-control-prev');
    const nextControl = document.querySelector('.carousel-control-next');
  
    prevControl.addEventListener('click', function() {
      changeCarouselItem(-1);
    });
  
    nextControl.addEventListener('click', function() {
      changeCarouselItem(1);
    });
  });
  