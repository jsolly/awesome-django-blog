function countCharacters() {
    function count(input, count) {
      const charCount = count.querySelector(".char-count");
      charCount.textContent = input.value.length;
      input.addEventListener("input", () => {
        charCount.textContent = input.value.length;
      });
    }
  
    const titleInput = document.querySelector("#id_title");
    const titleCount = document.querySelector("#title-count");
    count(titleInput, titleCount);
  
    const slugInput = document.querySelector("#id_slug");
    const slugCount = document.querySelector("#slug-count");
    count(slugInput, slugCount);
  
    const metadescInput = document.querySelector("#id_metadesc");
    const metadescCount = document.querySelector("#metadesc-count");
    count(metadescInput, metadescCount);
  }
  
  window.onload = countCharacters;