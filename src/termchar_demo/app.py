from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.events import DescendantBlur, Event
from textual.reactive import reactive
from textual.validation import Integer
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
    timeout: int = 2

    class DataOut(Event):
        def __init__(self, data: str) -> None:
            super().__init__()
            self.data = data

    class DataIn(Event):
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
                yield (
                    input := Input(
                        placeholder="Type termination characters here...",
                        id="read-termchars",
                    )
                )
                input.border_title = "Read Termination Characters"
                yield (
                    input := Input(
                        value=str(self.timeout),
                        id="timeout",
                        restrict="[0-9]*",
                        validators=Integer(minimum=0),
                    )
                )
                input.border_title = "Timeout"
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

    @on(Input.Submitted, "#timeout")
    @on(DescendantBlur, "#timeout")
    def set_timeout(self) -> None:
        widget: Input
        if not (widget := self.query_one("#timeout")).is_valid:
            widget.value = "0"
        self.timeout = int(widget.value)

    @on(Input.Submitted)
    @on(Button.Pressed, "#write-button")
    def send_data(self) -> None:
        termchars: Input = self.query_one("#write-termchars").value
        output: Input = self.query_one("#output")
        self.post_message(self.DataOut(output.value + termchars))
        output.clear()

    @on(DataOut)
    def log_write(self, event: DataOut) -> None:
        self.query_one("#log").write(f"[light_steel_blue1]> Sent {event.data}")
        # dark_olive_green1

    @on(DataIn)
    def fill_buffer(self, event: DataIn) -> None:
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

    @on(Client.DataOut)
    def send_to_server(self, event: Client.DataOut) -> None:
        self.query_one(Server).post_message(Server.DataIn(event.data))


app = TermCharDemo
if __name__ == "__main__":
    app().run()
