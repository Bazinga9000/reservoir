"use strict";

function initChat(puzzleId) {
  const chatLog = document.querySelector("#chat-log");
  const chatInput = document.querySelector("#chat-message-input");
  const chatSubmit = document.querySelector("#chat-message-submit");
  let latestMessageId = 0;

  // UI update functions =====================

  const dateFormatter = new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  });

  function appendNewMessage(message) {
    // ignore messages already received (e.g. in the race condition described
    // below in the connect() comment, messageQueue might contain some messages
    // already added through the history fetch; don't add those again)
    if (message.id <= latestMessageId) {
      return;
    }
    // if the above check passes, we can assume this is the latest message
    latestMessageId = message.id;

    const sentDate = new Date(message.sent_date);
    const elem = document.createElement("div");
    elem.className = "chat-msg";
    elem.innerHTML = `
      <span class="chat-msg-user"></span> <span class="chat-msg-date"></span><br />
      <span class="chat-msg-content"></span>
    `;

    var display_user;
    if (message.is_system) {
      display_user = "[System]"; 
    } else {
      display_user = message.username;
    }

    elem.querySelector(".chat-msg-user").textContent = display_user;
    elem.querySelector(".chat-msg-user").style.color = "var(--" + message.chat_color + ")"
    elem.querySelector(".chat-msg-date").textContent =
      dateFormatter.format(sentDate);

    renderMessage(message, elem.querySelector(".chat-msg-content"));

    chatLog.appendChild(elem);
    return elem;
  }

  function chatLogIsScrolledToBottom() {
    // https://stackoverflow.com/a/42860948
    return chatLog.scrollHeight - chatLog.scrollTop - chatLog.clientHeight < 1;
  }

  function scrollChatLogToBottom() {
    chatLog.scrollTop = chatLog.scrollHeight;
  }

  // websocket handling =====================

  const socketProtocol = location.protocol === "http:" ? "ws" : "wss";
  let chatSocket;

  function connect() {
    // ok, so i'm imagining a potential race condition where new individual
    // messages come in before the history arrives and gets populated, which
    // could lead to some mess. this is probably really unlikely, but to be
    // safe i'm gonna store these messages in a queue until the history arrives
    let historyPopulated = false;
    let messageQueue = [];

    chatSocket = new WebSocket(
      `${socketProtocol}://${window.location.host}/ws/chat/${puzzleId}/`,
    );

    chatSocket.onopen = (e) => {
      // request chat history
      chatSocket.send(
        JSON.stringify({
          type: "get_history",
          after: latestMessageId,
        }),
      );
    };

    chatSocket.onmessage = (e) => {
      const data = JSON.parse(e.data);

      if (data.type === "message") {
        if (!historyPopulated) {
          messageQueue.push(data.message);
        } else {
          const wasAtBottom = chatLogIsScrolledToBottom();
          appendNewMessage(data.message);
          if (wasAtBottom)
            scrollChatLogToBottom();
        }
      } else if (data.type == "history") {
        const wasAtBottom = chatLogIsScrolledToBottom();
        for (const message of data.messages) {
          appendNewMessage(message);
        }
        for (const message of messageQueue) {
          appendNewMessage(message);
        }
        historyPopulated = true;
        if (wasAtBottom)
          scrollChatLogToBottom();
      } else {
        console.error("Unknown message received:", data);
      }
    };

    chatSocket.onclose = (e) => {
      console.log("Socket closed, attempting reconnect in 1 second");
      setTimeout(() => {
        connect();
      }, 1000);
    };
  }

  connect();

  // UI event handling =====================

  chatInput.onkeyup = function (e) {
    if (e.key === "Enter" && !e.shiftKey) chatSubmit.click();
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

// Message rendering
function renderMessage(message, elem) {

  const entityMap = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
    '/': '&#x2F;',
  }

  function escapeHtml(html) {
    return html.replace(/[&<>"'/]/g, (key) => entityMap[key])
  }

  // render the markdown
  var content = message.content;
  content = content.replace(/^[\u200B\u200C\u200D\u200E\u200F\uFEFF]/,"");
  content = escapeHtml(content);

  elem.innerHTML = DOMPurify.sanitize(marked.parse(content, {gfm: true, breaks: true}))

  renderMathInElement(
    elem,
    {
      delimiters: [
        {left: "$$", right: "$$", display: true},
        {left: "\\[", right: "\\]", display: true},
        {left: "$", right: "$", display: false},
        {left: "\\(", right: "\\)", display: false}
      ],

      throwOnError: false
    }
  );
}
