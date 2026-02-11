"use strict";

function initChat(puzzleId) {
  const chatLog = document.querySelector("#chat-log");
  const chatInput = document.querySelector("#chat-message-input");
  const chatSubmit = document.querySelector("#chat-message-submit");

  // UI update functions

  function appendNewMessage(message) {
    const elem = document.createElement("p");
    elem.innerHTML = `
      <span class="chat-msg-user"></span><br />
      <span class="chat-msg-content"></span>
    `;
    elem.querySelector(".chat-msg-user").textContent = message.username;
    elem.querySelector(".chat-msg-content").textContent = message.content;

    chatLog.appendChild(elem);
    return elem;
  }

  // websocket handling
  const socketProtocol = location.protocol === "http:" ? "ws" : "wss";
  const chatSocket = new WebSocket(
    `${socketProtocol}://${window.location.host}/ws/chat/${puzzleId}/`,
  );

  chatSocket.onopen = (e) => {
    // fetch chat history
    chatSocket.send(JSON.stringify({ type: "get_history", after: 0 }));
  };

  chatSocket.onmessage = (e) => {
    const data = JSON.parse(e.data);

    console.log(data);

    if (data.type === "message") {
      appendNewMessage(data.message);
    } else if (data.type == "history") {
      for (const message of data.messages) {
        appendNewMessage(message);
      }
    } else {
      console.error("Unknown message received:", data);
    }
  };

  chatSocket.onclose = (e) => {
    console.error("Chat socket closed unexpectedly");
  };

  // UI event handling

  chatInput.onkeyup = function (e) {
    if (e.key === "Enter") chatSubmit.click();
  };

  chatSubmit.onclick = function (e) {
    if (chatInput.value) {
      // don't sent blank messages
      chatSocket.send(
        JSON.stringify({ type: "message", content: chatInput.value }),
      );
      chatInput.value = "";
    }
  };
}
