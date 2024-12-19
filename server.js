const express = require("express");
const http = require("http");
const WebSocket = require("ws");

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

let hostSocket = null;
let candidateSocket = null;

wss.on("connection", (ws, req) => {
  console.log("New connection established.");

  ws.on("message", (message) => {
    const data = JSON.parse(message);

    if (data.type === "candidate-video") {
      candidateSocket = ws;
      console.log("Candidate connected.");
    } else if (data.type === "host-video") {
      hostSocket = ws;
      console.log("Host connected.");
    } else if (data.type === "video-frame" && hostSocket) {
      hostSocket.send(data.frame); // Send the video frame to the host
    }
  });

  ws.on("close", () => {
    if (ws === candidateSocket) candidateSocket = null;
    if (ws === hostSocket) hostSocket = null;
    console.log("Connection closed.");
  });
});

// Serve static files (frontend pages)
app.use(express.static("public"));

const PORT = 3000;
server.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
