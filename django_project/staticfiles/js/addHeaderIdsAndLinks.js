function addHeaderIDs() {
  var headers = document.querySelectorAll("h1, h2, h3");
  for (const header of headers) {
    header.id = header.textContent
      .trim()
      .toLowerCase()
      .replace(/\s+/g, "-")
      .replace(/[^a-zA-Z0-9_\-]/g, "");
  }
}

function addHeaderLinks() {
  var headers = document.querySelectorAll("h1,h2,h3");
  for (const header of headers) {
    var headerId = header.getAttribute("id");
    var link = document.createElement("a");
    link.href = `#${headerId}`;
    link.classList.add("header-link");
    link.innerHTML = " 🔗";
    header.appendChild(link);
  }
  var links = document.querySelectorAll(".header-link");
  for (const link of links) {
    link.addEventListener("click", function () {
      var linkUrl = this.href;
      navigator.clipboard.writeText(linkUrl).then(
        function () {
          console.log("Link URL copied to clipboard!");
        },
        function (err) {
          console.log("Unable to copy link URL: ", err);
        }
      );
    });
  }
}

document.addEventListener("DOMContentLoaded", function () {
  addHeaderIDs();
  addHeaderLinks();
});
