from flask import Flask, render_template
import threading
import asyncio
import websockets
import json

# Flask apps
candidate_app = Flask(__name__)
host_app = Flask(__name__)

# Store WebSocket connections
candidate_socket = None
host_socket = None

@candidate_app.route("/")
def candidate_page():
    """Serve the candidate page."""
    return render_template("candidate.html")

@host_app.route("/")
def host_page():
    """Serve the host page."""
    return render_template("host.html")

async def handle_connection(websocket, path):
    """WebSocket connection handler."""
    global candidate_socket, host_socket

    async for message in websocket:
        data = json.loads(message)

        if data["type"] == "candidate-video":
            candidate_socket = websocket
        elif data["type"] == "host-video":
            host_socket = websocket
        elif data["type"] == "video-frame" and host_socket:
            # Forward candidate video to host
            if host_socket.open:
                await host_socket.send(data["frame"])

def start_websocket_server():
    """Start WebSocket server."""
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    server = websockets.serve(handle_connection, "localhost", 3001)
    loop.run_until_complete(server)
    print("WebSocket server running on ws://localhost:3001")
    loop.run_forever()

def run_candidate_server():
    """Run the candidate Flask server."""
    candidate_app.run(port=3000, use_reloader=False)

def run_host_server():
    """Run the host Flask server."""
    host_app.run(port=3002, use_reloader=False)

if __name__ == "__main__":
    # Start WebSocket server
    ws_thread = threading.Thread(target=start_websocket_server, daemon=True)
    ws_thread.start()

    # Start Flask servers
    candidate_thread = threading.Thread(target=run_candidate_server, daemon=True)
    candidate_thread.start()

    run_host_server()
