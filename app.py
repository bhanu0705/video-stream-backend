import asyncio
import websockets
from flask import Flask, send_from_directory
import threading
import json

# Flask app initialization
app = Flask(__name__)

# Store connections for host and candidate
host_socket = None
candidate_socket = None


@app.route('/<path:path>')
def serve_static(path):
    """
    Serve static files like HTML, CSS, JS, etc.
    """
    return send_from_directory('public', path)


async def handle_connection(websocket, path):
    """
    WebSocket connection handler.
    """
    global host_socket, candidate_socket
    print("New WebSocket connection established.")

    try:
        async for message in websocket:
            data = json.loads(message)

            if data['type'] == 'candidate-video':
                candidate_socket = websocket
                print("Candidate connected.")
            elif data['type'] == 'host-video':
                host_socket = websocket
                print("Host connected.")
            elif data['type'] == 'video-frame' and host_socket:
                # Forward video frames from candidate to host
                if host_socket.open:
                    await host_socket.send(data['frame'])
            else:
                print("Unrecognized message:", data)

    except websockets.exceptions.ConnectionClosed:
        print("WebSocket connection closed.")
        if websocket == candidate_socket:
            candidate_socket = None
        if websocket == host_socket:
            host_socket = None

def start_websocket_server():
    """
    Start the WebSocket server using asyncio in a thread-safe way.
    """
    # Set asyncio's event loop policy for compatibility in threads
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Run the WebSocket server in this event loop
    server = websockets.serve(handle_connection, 'localhost', 3001)
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
