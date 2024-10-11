const W = window.innerWidth;
const H = window.innerHeight;

let coords: { x: number; y: number }[] = [];

const canvas = document.getElementById("drawingCanvas") as HTMLCanvasElement;
const ctx = canvas.getContext("2d");

let isDrawing = false;

// Function to start drawing
const startDrawing = (event: MouseEvent) => {
  isDrawing = true;
  ctx?.beginPath();
  ctx?.moveTo(event.offsetX, event.offsetY);
};

// Function to draw on canvas
const draw = (event: MouseEvent) => {
  if (!isDrawing || !ctx) return;
  ctx.lineTo(event.offsetX, event.offsetY);
  ctx.stroke();
  coords.push({ x: event.offsetX, y: event.offsetY });
};

// Function to stop drawing
const stopDrawing = () => {
  isDrawing = false;
  ctx?.closePath();
  if (coords.length === 0) return;
  createThumbnail();
  console.log("DREW AN IMAGE", coords);
  ctx?.clearRect(0, 0, canvas.width, canvas.height);
  coords = [];
};

const createThumbnail = () => {
  // Generate a base64 image from the canvas
  const thumbnailSrc = canvas.toDataURL("image/png");

  // Create an img element for the thumbnail
  const img = document.createElement("img");
  img.src = thumbnailSrc;
  img.classList.add("thumbnail");
  img.width = 100; // Set thumbnail width
  img.height = 100; // Set thumbnail height

  // Append the img to the thumbnails container
  document.getElementById("thumbnailsContainer")?.appendChild(img);
};

const initialize = () => {
  canvas.addEventListener("mousedown", startDrawing);
  canvas.addEventListener("mousemove", draw);
  canvas.addEventListener("mouseup", stopDrawing);
  canvas.addEventListener("mouseout", stopDrawing);
};

document.addEventListener("DOMContentLoaded", (event) => {
  initialize();
});
