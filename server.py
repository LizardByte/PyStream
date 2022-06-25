# standard imports
from socket import socket
from threading import Thread
import time

# lib imports
from lz4.frame import compress
from mss import mss


def retrieve_screenshot(conn):
    with mss() as sct:
        # I believe 0 and -1 are all monitors... need to confirm
        monitor_number = 0
        mon = sct.monitors[monitor_number]

        # The region to capture
        monitor = dict(
            top=mon["top"],
            left=mon["left"],
            width=mon["width"],
            height=mon["height"],
            mon=monitor_number
        )

        while "Screen capturing":
            last_time = time.time()

            # use sct.grab to grab a portion of the screen
            img = sct.grab(monitor=monitor)

            # Tweak the compression level here (0-9)
            pixels = compress(img.rgb, 0)

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
            print(f"fps: {1 / (time.time() - last_time)}")


def main(host='0.0.0.0', port=5000):
    sock = socket()
    sock.bind((host, port))
    try:
        sock.listen(5)
        print('Server started.')

        while 'connected':
            conn, addr = sock.accept()
            print('Client connected IP:', addr)
            thread = Thread(target=retrieve_screenshot, args=(conn,))
            thread.start()
    finally:
        sock.close()


if __name__ == '__main__':
    main()
