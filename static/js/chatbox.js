document.addEventListener("DOMContentLoaded", () => {
  class Chatbox {
    constructor() {
      this.openButton = document.querySelector(".chatbox__button");
      this.chatBox = document.querySelector(".chatbox__support");
      this.sendButton = document.querySelector(".send__button");
      this.closeButton = document.querySelector(
        ".chatbox__close--header button"
      );
      this.state = false;
    }

    display() {
      this.openButton.addEventListener("click", () => this.toggleState());
      this.closeButton.addEventListener("click", () => this.toggleState());
      this.sendButton.addEventListener("click", () => this.onSendButton());
      const textArea = this.chatBox.querySelector("textarea");

      textArea.addEventListener("input", () => {
        textArea.style.height = "auto";
        textArea.style.height = `${textArea.scrollHeight}px`;
      });

      textArea.addEventListener("keyup", ({ key, shiftKey }) => {
        if (key === "Enter" && !shiftKey) {
          this.onSendButton();
        }
      });

      const observer = new MutationObserver(() => {
        textArea.style.height = "auto";
      });

      observer.observe(textArea, {
        childList: true,
        subtree: true,
        characterData: true,
      });
    }

    toggleState() {
      this.state = !this.state;
      this.chatBox.classList.toggle("chatbox--active", this.state);
      document.getElementById("chatbox-icon").style.display = this.state
        ? "none"
        : "block";
    }

    onSendButton() {
      const textField = this.chatBox.querySelector("#question-text-area");
      const text = textField.value.trim();
      if (text === "" || text === "\n") {
        return;
      }
      this.updateChatText(text);
      textField.value = "";
      textField.style.height = "auto";
      textField.dispatchEvent(new Event("input"));
    }

    updateChatText(text) {
      const chatmessages = this.chatBox.querySelector(".chatbox__messages");
      const message = document.createElement("div");
      message.classList.add("messages__item", "messages__item--user");
      message.textContent = text;
      chatmessages.prepend(message);
    }
  }

  const chatbox = new Chatbox();
  chatbox.display();
});
