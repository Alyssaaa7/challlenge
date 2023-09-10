import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.signaling import TcpSocketSignaling
import numpy as np
import cv2
'''
1. Make a server python program that runs from the command line(python3 server.py)
2. Make a client python program that runs from the command line(python3 client.py).
3. Using aiortcbuilt-inTcpSocketSignaling:
a. The server should create an aiortc offer and send to client.
b. The client should receive the offerand create an aiortc answer.
4. The server should generate a continuous 2D image/frames of a ball bouncing across the screen.
5. The server should transmit these images to the client via aiortc using frame transport (extend
aiortc.MediaStreamTrack).
6. The client should display the received images using opencv.
7. The client should start a newmultiprocessing.Process(process a).
8. The client should send the received frame to this process ausing amultiprocessing.Queue.
9. The client process a should parse the image and determine the current location of the ball as x,y
coordinates.
10.The client process_a should store the computed xy coordinate as a multiprocessing.Value.11.The client should open an aiortc data channel to the server and send each xy coordinate to the
server. These coordinates are from process a but sent to server from client main thread.
12.The server program should display the received coordinates and compute the error to the actual
location of the ball.
13. Document all code using python docstrings.
14.Write unit tests for all functions which will be executed by pytest(pytest test YOUR SCRIPT.Py)15. Include a README file.
16.Include a screen capture(mp4,mkv,avi,etc.) of your application in action.
17.Compress the project directory and include your name in the filename.Do not post solutions publicly.18.Docker Image:
a. Make a docker image(Dockerfile) for the server b. Make a docker image(Dockerfile) for the client
19. Kubernetes
a. Create kubernetes manifest yaml files for client and server deployment b. Docs for deployingit(usingminikube/k3s/microk8s etc.)
'''

class BallTrackStream:
    def __init__(self):
        self.width = 640
        self.height = 480
        self.ball_radius = 20
        self.ball_speed_x = 5
        self.ball_speed_y = 7
        self.ball_pos_x = 300
        self.ball_pos_y = 200
        self.ball_color = (255, 0, 0)
        self.ball_thickness = 2

    async def draw_frame(self):
        frame = np.zeros((self.height, self.width, 3), np.uint8)
        self.ball_pos_x += self.ball_speed_x
        self.ball_pos_y += self.ball_speed_y
        if self.ball_pos_x < self.ball_radius or self.ball_pos_x > self.width - self.ball_radius:
            self.ball_speed_x = -self.ball_speed_x
        if self.ball_pos_y < self.ball_radius or self.ball_pos_y > self.height - self.ball_radius:
            self.ball_speed_y = -self.ball_speed_y
        cv2.circle(frame, (self.ball_pos_x, self.ball_pos_y), self.ball_radius, self.ball_color, self.ball_thickness)
        return frame


async def run(server):
    pc = RTCPeerConnection()
    @pc.on("datachannel")
    async def on_data_channel(channel):
        @channel.on("message")
        def on_message(message):
            print("Message received:", message)
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)
        await server.send(str(pc.localDescription.sdp))

        answer = await server.receive()
        await pc.setRemoteDescription(RTCSessionDescription(sdp=answer, type="answer"))
        print("Answer received and set.")


        stream = BallTrackStream()
        while True:
            frame = await stream.draw_frame()
            channel.send(frame)
            await asyncio.sleep(0.1)

    await server.close()
    await pc.close()



if __name__ == "__main__":
    server = TcpSocketSignaling()
    asyncio.run(run(server))








