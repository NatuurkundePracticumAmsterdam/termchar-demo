from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical

from termchar_demo.arrows import Arrows
from termchar_demo.devices import Device


class Client(Device):
    BORDER_TITLE: str = "Client"


class Server(Device):
    BORDER_TITLE: str = "Server"
    TIMEOUT = 0

    def compose(self) -> ComposeResult:
        with Vertical(id="container"):
            yield from self.input_widgets()
            yield from self.log_widget()
            yield from self.output_widgets()

    def on_mount(self) -> None:
        self.query_one("#read-termchars").value = r"\n"
        self.query_one("#write-termchars").value = r"\r\n"


class AdvancedDemo(Container):
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Client()
            yield Arrows()
            yield Server()

    @on(Device.DataOut)
    def send_data(self, event: Device.DataOut) -> None:
        if event.sender == self.query_one(Client):
            target = Server
        else:
            target = Client
        self.query_one(target).post_message(Device.DataIn(event.data))
