import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.signaling import TcpSocketSignaling
import logging
logging.basicConfig(level=logging.DEBUG)
is_channel_open = False  # Global flag

async def run():
    global is_channel_open

    print("Server starting...")
    signaling = TcpSocketSignaling('127.0.0.1', 1234)
    await signaling.connect()
    print("Connected to signaling server.")

    pc = RTCPeerConnection(configuration={"iceServers": []})

    data_channel = pc.createDataChannel("chat")

    def on_data_channel_open():
        global is_channel_open
        is_channel_open = True
        print("Data channel is open")
        data_channel.send("Hello from server!")

    data_channel.on("open", on_data_channel_open)
    data_channel.on("message", lambda message: print("Received message:", message))

    # Create an offer
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    print("Offer created.")

    # Send the offer
    await signaling.send(offer)
    print("Offer sent.")

    # Wait for answer
    answer = await signaling.receive()
    await pc.setRemoteDescription(answer)
    print("Answer received and set.")

    # Here, we wait for the data channel to open before proceeding
    while not is_channel_open:
        await asyncio.sleep(1)

    try:
        await asyncio.sleep(60)  # Keep the server alive for 60 seconds
    except asyncio.CancelledError:
        pass

    await signaling.close()
    print("Server closed.")

if __name__ == "__main__":
    asyncio.run(run())
