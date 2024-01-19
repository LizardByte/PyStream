# standard imports
from socket import socket

# kivy imports
from kivy.config import Config
from kivy.core.window import Window
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

# lib imports
from lz4.frame import decompress
import pygame

Config.set('graphics', 'resizable', 0)
Window.size = (1280, 720)

kv = '''
Main:
    BoxLayout:
        orientation: 'vertical'
        padding: root.width * 0.05, root.height * .05
        spacing: '5dp'
        BoxLayout:
            size_hint: [1,.85]
            Image:
                id: image
                source: 'foo.png'
        BoxLayout:
            size_hint: [1,.15]
            GridLayout:
                cols: 3
                spacing: '10dp'
                Button:
                    id: status
                    text:'Play'
                    bold: True
                    on_press: root.play_pause()
                Button:
                    text: 'Close'
                    bold: True
                    on_press: root.close()
                Button:
                    text: 'Setting'
                    bold: True
                    on_press: root.setting()
'''


def recv_all(conn, length):
    """Retrieve all pixels."""

    buf = b''
    while len(buf) < length:
        data = conn.recv(length - len(buf))
        if not data:
            return data
        buf += data
    return buf


class Main(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server_address = None
        self.server_port = None
        self.server_input = None
        self.port_input = None
        self.popup = None
        self.sock = socket()

    def play_pause(self):
        if not self.server_address or not self.server_port:
            box = GridLayout(cols=1)
            box.add_widget(Label(text="Ip or Port Not Set"))
            btn = Button(text="OK")
            btn.bind(on_press=self.close_popup)
            box.add_widget(btn)
            self.popup = Popup(title='Error', content=box, size_hint=(.8, .3))
            self.popup.open()
        else:
            if self.ids.status.text == "Stop":
                self.stop()
            else:
                self.sock = socket()
                self.sock.connect((self.server_address, self.server_port))
                self.ids.status.text = "Stop"
                Clock.schedule_interval(self.recv, 0.05)

    def close_popup(self, btn):
        self.popup.dismiss()

    def stop(self):
        Clock.unschedule(self.recv)
        self.sock.close()
        self.ids.status.text = "Play"

    def recv(self, dt):
        size_len = int.from_bytes(self.sock.recv(1), byteorder='big')
        size = int.from_bytes(self.sock.recv(size_len), byteorder='big')
        pixels = decompress(recv_all(self.sock, size))

        image = pygame.image.fromstring(pixels, (1920, 1080), "RGB")  # convert received image from string

        try:
            pygame.image.save(image, "foo.png")
            self.ids.image.reload()
        except:
            pass

    def close(self):
        App.get_running_app().stop()

    def setting(self):
        box = GridLayout(cols=2)
        box.add_widget(Label(text="IpAddress: ", bold=True))
        self.server_input = TextInput()
        box.add_widget(self.server_input)
        box.add_widget(Label(text="Port: ", bold=True))
        self.port_input = TextInput()
        box.add_widget(self.port_input)
        btn = Button(text="Set", bold=True)
        btn.bind(on_press=self.setting_save)
        box.add_widget(btn)
        self.popup = Popup(title='Settings', content=box, size_hint=(.6, .4))
        self.popup.open()

    def setting_save(self, btn):
        # todo - validate ip address and port
        try:
            self.server_address = self.server_input.text
            self.server_port = int(self.port_input.text)
        except:
            pass
        self.popup.dismiss()


class PyStreamApp(App):
    def build(self):
        return Builder.load_string(kv)


PyStreamApp().run()
