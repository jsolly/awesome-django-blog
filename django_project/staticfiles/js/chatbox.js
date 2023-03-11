document.addEventListener("DOMContentLoaded", function () {
  class Chatbox {
    constructor() {
      this.args = {
        openButton: document.querySelector(".chatbox__button"),
        chatBox: document.querySelector(".chatbox__support"),
        sendButton: document.querySelector(".send__button"),
      };

      this.state = false;
    }

    display() {
      const { openButton, chatBox, sendButton } = this.args;

      openButton.addEventListener("click", () => this.toggleState(chatBox));
      sendButton.addEventListener("click", () => this.onSendButton(chatBox));

      const node = chatBox.querySelector("textarea");
      node.addEventListener("input", () => {
        node.style.height = "auto";
        node.style.height = `${node.scrollHeight}px`;
      });

      node.addEventListener("keyup", ({ key, shiftKey }) => {
        if (key === "Enter" && !shiftKey) {
          this.onSendButton(chatBox);
        }
      });
    }

    toggleState(chatbox) {
      this.state = !this.state;

      // show or hides the box
      if (this.state) {
        chatbox.classList.add("chatbox--active");
      } else {
        chatbox.classList.remove("chatbox--active");
      }
    }

    onSendButton(chatbox) {
      var textField = chatbox.querySelector("#question-text-area");
      let text1 = textField.value.trim();
      if (text1 === "" || text1 === "\n") {
        return;
      }

      this.updateChatText(chatbox, text1);
    }

    updateChatText(chatbox, text) {
      const chatmessages = chatbox.querySelector(".chatbox__messages");
      const message = document.createElement("div");
      message.className = "messages__item messages__item--user";
      message.textContent = text;
      chatmessages.prepend(message);
      chatbox.querySelector("#question-text-area").value = "";
    }
  }

  const chatbox = new Chatbox();
  chatbox.display();
});
