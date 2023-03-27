document.addEventListener("DOMContentLoaded", () => {
  class Chatbox {
    constructor() {
      this.openButton = document.querySelector(".chatbox__button");
      this.chatBox = document.querySelector(".chatbox__support");
      this.sendButton = document.querySelector(".send__button");
      this.state = false;
    }

    display() {
      this.openButton.addEventListener("click", () => this.toggleState());
      this.sendButton.addEventListener("click", () => this.onSendButton());

      const node = this.chatBox.querySelector("textarea");
      node.addEventListener("input", () => {
        node.style.height = "auto";
        node.style.height = `${node.scrollHeight}px`;
      });

      node.addEventListener("keyup", ({ key, shiftKey }) => {
        if (key === "Enter" && !shiftKey) {
          this.onSendButton();
        }
      });
    }

    toggleState() {
      this.state = !this.state;

      // show or hides the box
      this.chatBox.classList.toggle("chatbox--active", this.state);
    }

    onSendButton() {
      const textField = this.chatBox.querySelector("#question-text-area");
      const text = textField.value.trim();
      if (text === "" || text === "\n") {
        return;
      }

      this.updateChatText(text);
    }

    updateChatText(text) {
      const chatmessages = this.chatBox.querySelector(".chatbox__messages");
      const message = document.createElement("div");
      message.classList.add("messages__item", "messages__item--user");
      message.textContent = text;
      chatmessages.prepend(message);
      this.chatBox.querySelector("#question-text-area").value = "";
    }
  }

  const chatbox = new Chatbox();
  chatbox.display();
});
