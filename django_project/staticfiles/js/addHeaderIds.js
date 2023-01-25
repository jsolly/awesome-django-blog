function addHeaderIDs() {
  var headers = document.querySelectorAll("h2, h3");
  headers.forEach(header => {
    header.id = header.textContent.toLowerCase().replace(/\s+/g, '-').replace(/[^a-zA-Z0-9_\-]/g,'');
  });
}

window.onload = addHeaderIDs;