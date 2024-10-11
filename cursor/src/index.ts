const reconnectInterval = 3000; // Time (in ms) to wait before attempting to reconnect
let websocket: WebSocket | null = null;

function stringToColor(str: string): string {
  // Create a hash from the string
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }

  // Convert the hash to a hex color
  let color = "#";
  for (let i = 0; i < 3; i++) {
    const value = (hash >> (i * 8)) & 0xff;
    color += value.toString(16).padStart(2, "0");
  }

  return color;
}
function connect() {
  websocket = new WebSocket("ws://localhost:8080/");

  websocket.onopen = () => {
    console.log("WebSocket connection established");
  };

  websocket.onmessage = ({ data }) => {
    const obj = JSON.parse(data);
    const id = obj.client;
    document.getElementById(id)?.remove();

    // create a div with class dot
    const dot = document.createElement("div");
    // set html property id of dot
    dot.id = id;
    // add class dot to the dot
    dot.classList.add("dot");
    dot.innerText = id;
    // set the position of the dot
    dot.style.left = `${obj.x}px`;
    dot.style.top = `${obj.y}px`;
    dot.style.backgroundColor = stringToColor(id);
    // append the dot to the body
    document.body.appendChild(dot);
    setTimeout(() => {
      dot?.remove();
    }, 30000);
  };

  websocket.onclose = (event) => {
    console.log(
      `WebSocket connection closed (code: ${event.code}), attempting to reconnect in ${reconnectInterval / 1000} seconds...`,
    );
    setTimeout(() => {
      connect();
    }, reconnectInterval);
  };

  websocket.onerror = (error) => {
    console.error("WebSocket encountered error:", error);
    websocket?.close();
  };
}

document.addEventListener("DOMContentLoaded", () => {
  connect();

  const captureMouseMove = (event: MouseEvent) => {
    const message = {
      x: event.pageX,
      y: event.pageY,
      width: window.innerWidth,
      height: window.innerHeight,
    };
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      console.log("Sending message", message);
      // Sending a message to the WebSocket server
      websocket.send(JSON.stringify(message));
    } else {
      console.log("Cannot send message: WebSocket connection is not open");
    }
  };

  document.body.addEventListener("mousemove", captureMouseMove);
});
