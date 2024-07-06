from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.events import Event
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Input, Label, RichLog


class Buffer(Label):
    data: str

    def __init__(self, data: str = "", *args, **kwargs) -> None:
        super().__init__(data, *args, **kwargs)
        self.data = data

    def append(self, new_data: str) -> None:
        self.data += new_data
        self.update(self.data)


class Device(Container):
    is_busy_read = reactive(False)

    class SendData(Event):
        def __init__(self, data: str) -> None:
            super().__init__()
            self.data = data

    class NewData(Event):
        def __init__(self, data: str) -> None:
            super().__init__()
            self.data = data

    BORDER_TITLE: str = "Device"

    def compose(self) -> ComposeResult:
        with Vertical(id="container"):
            yield Input(id="output")
            with Horizontal():
                yield (input := Input(id="write-termchars"))
                input.border_title = "Write Termination Characters"
                yield Button("Write", id="write-button", variant="primary")
            yield (log := RichLog(id="log", markup=True))
            log.border_title = "Application Log"
            yield (label := Buffer(id="input-buffer"))
            label.border_title = "Input Buffer"
            with Horizontal():
                yield (input := Input(id="read-termchars"))
                input.border_title = "Read Termination Characters"
                yield Button("Read", id="read-button", variant="primary")

    def watch_is_busy_read(self, is_busy_read: bool) -> None:
        if is_busy_read:
            output: Input = self.query_one("#output")
            output.disabled = True
            output.placeholder = "Busy reading..."
            output.add_class("busy")
        else:
            output: Input = self.query_one("#output")
            output.disabled = False
            output.placeholder = "Type here to send data"
            output.remove_class("busy")

    @on(Input.Submitted)
    @on(Button.Pressed, "#write-button")
    def send_data(self) -> None:
        termchars: Input = self.query_one("#write-termchars").value
        output: Input = self.query_one("#output")
        self.post_message(self.SendData(output.value + termchars))
        output.clear()

    @on(SendData)
    def log_write(self, event: SendData) -> None:
        self.query_one("#log").write(f"[light_steel_blue1]> Sent {event.data}")
        # dark_olive_green1

    @on(NewData)
    def fill_buffer(self, event: NewData) -> None:
        buffer: Buffer = self.query_one("#input-buffer")
        buffer.append(event.data)


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
        self.query_one(Server).post_message(Server.NewData(event.data))


app = TermCharDemo
if __name__ == "__main__":
    app().run()
