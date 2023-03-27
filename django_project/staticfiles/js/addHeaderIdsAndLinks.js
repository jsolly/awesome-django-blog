const addHeaderIDs = () => {
  const headers = document.querySelectorAll("h1, h2, h3");
  headers.forEach((header) => {
    header.id = header.textContent
      .trim()
      .toLowerCase()
      .replace(/\s+/g, "-")
      .replace(/[^a-zA-Z0-9_\-]/g, "");
  });
};

const addHeaderLinks = () => {
  const headers = document.querySelectorAll("h1, h2, h3");
  headers.forEach((header) => {
    const headerId = header.getAttribute("id");
    const link = document.createElement("a");
    link.href = `#${headerId}`;
    link.classList.add("header-link");
    link.innerHTML = " 🔗";
    header.appendChild(link);
    link.addEventListener("click", () => {
      const linkUrl = link.href;
      navigator.clipboard.writeText(linkUrl).then(
        () => {
          console.log("Link URL copied to clipboard!");
        },
        (err) => {
          console.log("Unable to copy link URL: ", err);
        }
      );
    });
  });
};

document.addEventListener("DOMContentLoaded", () => {
  addHeaderIDs();
  addHeaderLinks();
});
