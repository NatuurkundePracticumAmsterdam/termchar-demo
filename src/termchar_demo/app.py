from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.events import Event
from textual.widgets import Button, Footer, Header, Input, Label, RichLog


class Device(Container):
    class SendData(Event):
        def __init__(self, data: str, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.data = data

    BORDER_TITLE: str = "Device"

    def compose(self) -> ComposeResult:
        with Vertical(id="container"):
            yield Input(placeholder="Send characters", id="output")
            yield (input := Input(id="write-termchars"))
            input.border_title = "Write Termination Characters"
            yield (log := RichLog(id="log"))
            log.border_title = "Application Log"
            yield (label := Label(id="input-buffer"))
            label.border_title = "Input Buffer"
            yield (input := Input(id="read-termchars"))
            input.border_title = "Read Termination Characters"

    @on(Input.Submitted)
    def send_data(self, event: Input.Submitted) -> None:
        termchars: Input = self.query_one("#write-termchars").value
        self.post_message(self.SendData(event.input.value + termchars))
        event.input.clear()


class Client(Device):
    BORDER_TITLE: str = "Client"


class Server(Device):
    BORDER_TITLE: str = "Server"


class TermCharDemo(App[None]):
    CSS_PATH = "app.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with Horizontal():
            yield Client()
            yield Server()

    @on(Client.SendData)
    def send_to_server(self, event: Client.SendData) -> None:
        buffer: Label = self.query_one(Server).query_one("#input-buffer")
        buffer.update(event.data)


TermCharDemo().run()
