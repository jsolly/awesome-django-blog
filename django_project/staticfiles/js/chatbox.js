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

      const node = chatBox.querySelector("input");
      node.addEventListener("keyup", ({ key }) => {
        if (key === "Enter") {
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
      var textField = chatbox.querySelector("#question-input");
      let text1 = textField.value;
      if (text1 === "") {
        return;
      }

      this.updateChatText(chatbox, text1);
    }

    updateChatText(chatbox, text) {
      const chatmessage = chatbox.querySelector('.chatbox__messages');
        const message = document.createElement('div');
        message.className = 'messages__item messages__item--operator';
        message.textContent = text;
        chatmessage.prepend(message);
        chatbox.querySelector("#question-input").value = "";
    }
  }
  
  const chatbox = new Chatbox();
  chatbox.display();
});
