import { useRef, useState, type MouseEvent } from "react";

export const Streamer = () => {
  const ref = useRef<HTMLDivElement | null>(null);
  const [message, setMessage] = useState("Tell me a three paragraph joke");

  const handleClick = async (e: MouseEvent) => {
    e.preventDefault();

    if (!ref.current) {
      return;
    }

    const response = await fetch(`http://localhost:5000/ask?q=${message}`, {
      method: "POST",
    });
    ref.current.innerHTML = "";

    if (!response.ok || !response.body) {
      console.error("Error:", response.statusText);
      return;
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const text = decoder.decode(value);
      console.error("Received chunk:", text);
      ref.current.innerHTML += text;
    }
  };

  return (
    <div>
      <form>
        <input
          type="text"
          placeholder="Enter your message"
          onChange={(e) => setMessage(e.target.value)}
          value={message}
          style={{ minWidth: "400px", marginRight: "8px" }}
        />
        <button type="submit" onClick={handleClick}>
          Send
        </button>
      </form>
      <code ref={ref} />
    </div>
  );
};
