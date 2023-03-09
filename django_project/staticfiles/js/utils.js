// document.addEventListener("DOMContentLoaded", function () {
//   const chatBox = document.querySelector(".chatbox__support");
//   let chatMessages = chatBox.querySelector(".chatbox__messages");
//   let scrollPosition = 0;

//   chatMessages.addEventListener("scroll", function () {
//     scrollPosition = chatMessages.scrollTop;
//   });

//   document.body.addEventListener("htmx:afterSwap", function (evt) {
//     if (evt.detail.trigger === "chatbox-submit") {
//       const newChatMessages = chatBox.querySelector(".chatbox__messages");
//       const newScrollHeight = newChatMessages.scrollHeight;
//       chatBox.scrollTop = newScrollHeight - scrollPosition;
//       chatMessages = newChatMessages;
//     }
//   });
// });
