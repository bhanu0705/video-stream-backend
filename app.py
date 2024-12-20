import asyncio
import websockets
from flask import Flask, render_template, jsonify
import threading
import json

# Flask app initialization
app = Flask(__name__)

# Store connections for host and candidate
host_socket = None
candidate_socket = None


@app.route("/")
def home():
    """Serve the candidate page as the default."""
    return render_template("candidate.html")


@app.route("/host")
def host_page():
    """Serve the host page."""
    return render_template("host.html")


async def handle_connection(websocket, path):
    """WebSocket connection handler."""
    global host_socket, candidate_socket
    print("New WebSocket connection established.")

    try:
        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "candidate-video":
                candidate_socket = websocket
                print("Candidate connected.")
            elif data["type"] == "host-video":
                host_socket = websocket
                print("Host connected.")
            elif data["type"] == "video-frame" and host_socket:
                # Forward video frames from candidate to host
                if host_socket.open:
                    await host_socket.send(data["frame"])
            else:
                print("Unrecognized message:", data)

    except websockets.exceptions.ConnectionClosed:
        print("WebSocket connection closed.")
        if websocket == candidate_socket:
            candidate_socket = None
        if websocket == host_socket:
            host_socket = None


def start_websocket_server():
    """Start the WebSocket server using asyncio in a thread-safe way."""
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Run the WebSocket server in this event loop
    server = websockets.serve(handle_connection, "localhost", 3001)
    loop.run_until_complete(server)
    print("WebSocket server running on ws://localhost:3001")
    loop.run_forever()


# Start Flask app and WebSocket server concurrently
if __name__ == "__main__":
    # Start WebSocket server in a separate thread
    ws_thread = threading.Thread(target=start_websocket_server, daemon=True)
    ws_thread.start()

    # Start Flask server
    print("Flask server running on http://localhost:3000")
    app.run(port=3000, use_reloader=False)
