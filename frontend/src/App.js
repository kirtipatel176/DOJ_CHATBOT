// src/App.js
import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    { text: "Hi there! How can I help you?", sender: "bot" },
  ]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const highlightKeywords = (text) => {
    const keywords = [
      "penalty", "court", "fine", "section", "IPC", "CRPC",
      "Motor Vehicles Act", "case", "legal", "law"
    ];
    const regex = new RegExp(`\\b(${keywords.join("|")})\\b`, "gi");

    return text.split(regex).map((part, idx) =>
      keywords.some(k => k.toLowerCase() === part.toLowerCase()) ? (
        <span key={idx} className="highlight">{part}</span>
      ) : (
        part
      )
    );
  };

  const formatBotResponse = (text) => {
    const paragraphs = text.split(/\n{2,}/); // Split by double newlines for new paragraphs

    return paragraphs.map((para, idx) => {
      const trimmed = para.trim();
      // If it looks like a list
      if (/^\s*[\d\-•]/.test(trimmed)) {
        const lines = trimmed.split("\n").filter(line => line.trim());
        return (
          <ul key={idx}>
            {lines.map((line, i) => (
              <li key={i}>
                {highlightKeywords(line.replace(/^[-•\d.]+\s*/, ""))}
              </li>
            ))}
          </ul>
        );
      } else {
        return <p key={idx}>{highlightKeywords(trimmed)}</p>;
      }
    });
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { text: input, sender: "user" };
    setMessages(prev => [...prev, userMessage]);
    setInput("");

    try {
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });

      if (!response.ok) throw new Error("Failed to fetch");

      const data = await response.json();
      const botReply = data.reply || "Sorry, I didn't understand that.";
      setMessages(prev => [...prev, { text: botReply, sender: "bot" }]);
    } catch (error) {
      console.error("Error:", error);
      setMessages(prev => [...prev, { text: "Server error. Try again later.", sender: "bot" }]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  return (
    <div className="chat-container">
      <header className="chat-header">Judiciary Chatbot</header>

      <div className="chat-box">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.sender}`}>
            {msg.sender === "bot"
              ? formatBotResponse(msg.text)
              : <p>{msg.text}</p>}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Type a legal question..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}

export default App;
 