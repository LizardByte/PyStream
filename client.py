# standard imports
from pickle import FRAME
from socket import socket
import numpy as np
import time

# lib imports
from lz4.frame import decompress
import cv2

# this display to show on
display = 0

# todo - allow different resolution than server output
WIDTH = 1920
HEIGHT = 1080


def recv_all(conn, length):
    """ Retrieve all pixels. """

    buf = b''
    while len(buf) < length:
        data = conn.recv(length - len(buf))
        if not data:
            return data
        buf += data
    return buf


def main(host='127.0.0.1', port=5000):
    sock = socket()
    sock.connect((host, port))

    # Receive Dimension of Stream
    dimension = (0, 0)
    dimension = str(sock.recv(1024), encoding='utf8').split("x")
    dimension = (int(dimension[0]), int(dimension[1]))
    print(f"Stream dimension: {dimension[0]}x{dimension[1]}")

    
    prevFrameTime = 0
    font = cv2.FONT_HERSHEY_SIMPLEX
    while True:
        #FPS 
        newFrameTime = time.time()
        fps = 1/(newFrameTime-prevFrameTime)
        prevFrameTime = newFrameTime

        # Retrieve the size of the pixels length, the pixels length and pixels
        size_len = int.from_bytes(sock.recv(1), byteorder='big')
        size = int.from_bytes(sock.recv(size_len), byteorder='big')
        pixels = decompress(recv_all(sock, size))

        # Display the picture
        frame = np.frombuffer(pixels, dtype=np.uint8)
        frame = np.reshape(frame, (dimension[1], dimension[0], 3))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Resize image
        frame = cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_AREA)

        # Display FPS
        cv2.putText(frame, str(int(fps)), (5, 30), font, 1, (255, 255, 0), 3, cv2.LINE_AA)

        
        
        # Output  to CV2q
        cv2.imshow("Output Frame", frame)

        # Check for 'q' key if pressed
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    #close connection
    sock.close()
    cv2.destroyAllWindows


if __name__ == '__main__':
    main(host='192.168.0.109')
