# standard imports
from socket import socket
from threading import Thread
import time

# lib imports
from lz4.frame import compress
from mss import mss
from vidgear.gears import ScreenGear
import cv2

fallback = 'mss'
monitor_number = 0

# Monitor setup
sct = mss()
mon = sct.monitors[monitor_number]
monitor = {
    'top': mon["top"],
    'left': mon["left"],
    'width': mon['width'],
    'height': mon['height'],
    'mon': monitor_number
}

# Initialize ScreenGear
stream = ScreenGear(**monitor, backend="mss")
stream.color_space = cv2.COLOR_BGR2RGB
stream.start()

def retrieve_screenshot(conn):
    
    # Send Dimension of Stream
    conn.sendall(bytes(f'{monitor["width"]}x{monitor["height"]}', encoding='utf8'))

    while True:
        last_time = time.perf_counter()

        # Capture the screen
        frame = stream.read()
        if frame is None:
            break

        # Tweak the compression level here (0-9)
        pixels = compress(frame, 0)

        # Send the size of the pixels length
        size = len(pixels)
        size_len = (size.bit_length() + 7) // 8

        # Sending through sockets
        try:
            conn.send(bytes([size_len]))

            # Send the actual pixels length
            size_bytes = size.to_bytes(size_len, 'big')
            conn.send(size_bytes)


            # Send pixels
            conn.sendall(pixels)
        except:
            break

        # print fps to terminal
        print(f"{1 / (time.perf_counter() - last_time)}")
    
    #Stop screen capture
    stream.stop()

def main(host='0.0.0.0', port=5000):
    
    # Connection
    sock = socket()
    sock.bind((host, port))
    
    try:
        sock.listen(5)
        print('Server started.')

        while True:
            conn, addr = sock.accept()
            print('Client connected IP:', addr)
            
            thread = Thread(target=retrieve_screenshot, args=(conn,))
            thread.start()

            
    finally:
        sock.close()


if __name__ == '__main__':
    main()
