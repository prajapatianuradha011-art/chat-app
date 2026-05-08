
import React, { useEffect, useState, useRef } from "react";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [username, setUsername] = useState("User");

  const socketRef = useRef(null);

  useEffect(() => {
    socketRef.current = new WebSocket("ws://127.0.0.1:8000/ws");

    socketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);

      setMessages((prev) => {
        if (data.streaming) {
          const updated = [...prev];

          updated[updated.length - 1] = data;

          return updated;
        }

        return [...prev, data];
      });
    };

    return () => socketRef.current.close();
  }, []);

  const sendMessage = () => {
    if (!text) return;

    socketRef.current.send(
      JSON.stringify({
        username,
        text,
      })
    );

    setMessages((prev) => [
      ...prev,
      {
        username,
        text: "",
        streaming: true,
      },
    ]);

    setText("");
  };

  const clearChat = async () => {
    await fetch("http://127.0.0.1:8000/clear", {
      method: "DELETE",
    });

    setMessages([]);
  };

  return (
    <div className="app">
      <div className="sidebar">
        <h2>Chat App</h2>

        <input
          placeholder="Your name"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <button onClick={clearChat}>
          Clear Chat
        </button>
      </div>

      <div className="chat-container">
        <div className="messages">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={
                msg.username === username
                  ? "my-message"
                  : "other-message"
              }
            >
              <strong>{msg.username}</strong>
              <p>{msg.text}</p>
            </div>
          ))}
        </div>

        <div className="input-bar">
          <input
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Type message..."
          />

          <button onClick={sendMessage}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;