# standard imports
from socket import socket
from threading import Thread
import platform
import time

# lib imports
from lz4.frame import compress
from mss import mss
import numpy as np
from PIL import ImageGrab

fallback = 'mss'
monitor_number = 0

# set up capture method
if platform.system() == 'Windows':
    import dxcam
    camera = dxcam.create(max_buffer_len=512)  # returns a DXCamera instance on primary monitor
else:
    camera = None
    sct = mss()

    mon = sct.monitors[monitor_number]

    # The region to capture
    monitor = dict(
        top=mon["top"],
        left=mon["left"],
        width=mon["width"],
        height=mon["height"],
        mon=monitor_number
    )


def image_capture():
    frame = None
    if camera:
        frame = np.array(camera.get_latest_frame())
    elif fallback == 'mss':
        frame = sct.grab(monitor=monitor).rgb
    elif fallback == 'pil':
        frame = np.array(ImageGrab.grab())

    return frame


def retrieve_screenshot(conn):

    while True:
        last_time = time.perf_counter()

        # Capture the screen
        frame = image_capture()

        if frame is None:
            break

        # Tweak the compression level here (0-9)
        pixels = compress(frame, 0)

        # Send the size of the pixels length
        size = len(pixels)
        size_len = (size.bit_length() + 7) // 8
        conn.send(bytes([size_len]))

        # Send the actual pixels length
        size_bytes = size.to_bytes(size_len, 'big')
        conn.send(size_bytes)

        # Send pixels
        conn.sendall(pixels)

        # print fps to terminal
        print(f"{1 / (time.perf_counter() - last_time)}")


def main(host='0.0.0.0', port=5000):
    sock = socket()
    sock.bind((host, port))
    try:
        sock.listen(5)
        print('Server started.')

        while True:
            conn, addr = sock.accept()
            print('Client connected IP:', addr)
            if camera:
                camera.start(target_fps=140)
            thread = Thread(target=retrieve_screenshot, args=(conn,))
            thread.start()
    finally:
        sock.close()
        if camera:
            camera.stop()


if __name__ == '__main__':
    main()
