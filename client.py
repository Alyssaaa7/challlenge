import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.signaling import TcpSocketSignaling
import logging
logging.basicConfig(level=logging.DEBUG)
async def run():
    print("Client starting...")
    signaling = TcpSocketSignaling('127.0.0.1', 1234)
    await signaling.connect()
    print("Connected to signaling server.")

    pc = RTCPeerConnection(configuration={"iceServers": []})


    def on_data_channel(channel):
        print(f"Data channel {channel.label} is open")
        channel.on("message", lambda message: print(f"Received message from {channel.label}: {message}"))
        channel.on("close", lambda: print(f"Data channel {channel.label} is closed"))

    pc.on("datachannel", on_data_channel)

    # Wait for offer
    offer = await signaling.receive()
    await pc.setRemoteDescription(offer)
    print("Offer received and set.")

    # Create an answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    print("Answer created.")

    # Send the answer
    await signaling.send(answer)
    print("Answer sent.")

    try:
        await asyncio.sleep(60)  # Keep the client alive for 60 seconds
    except asyncio.CancelledError:
        pass

    await signaling.close()
    print("Client closed.")

if __name__ == "__main__":
    asyncio.run(run())
