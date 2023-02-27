document.addEventListener('DOMContentLoaded', function() {
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        if (evt.target.className === 'chatbox__messages htmx-settling') {
            var input = document.getElementById('question-input');
            input.value = '';
          }
    });
  });
  