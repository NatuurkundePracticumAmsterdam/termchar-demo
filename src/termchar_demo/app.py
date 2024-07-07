from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.events import DescendantBlur, Event
from textual.reactive import reactive
from textual.timer import Timer
from textual.validation import Integer
from textual.widgets import Button, Footer, Header, Input, Label, RichLog


class Buffer(Label):
    data = reactive("")

    def __init__(self, data: str = "", length: int = 30, *args, **kwargs) -> None:
        super().__init__(data, *args, **kwargs)
        self.length = length
        self.data = data
        self.styles.max_width = self.length + 2

    def render(self) -> str:
        return self.data

    def append(self, new_data: str) -> None:
        self.data = (self.data + new_data)[: self.length]

    def watch_data(self):
        fill_factor = len(self.data) / self.length
        if fill_factor >= 0.8:
            self.set_classes("full")
        elif fill_factor >= 0.6:
            self.set_classes("almost-full")
        else:
            self.set_classes("")

    def read(self, termchars: str) -> str | None:
        if not termchars:
            if self.data:
                data = self.data
                self.data = ""
                return data
            else:
                return None

        if termchars in self.data:
            msg, self.data = self.data.split(termchars, maxsplit=1)
            return msg
        else:
            return None


class Device(Container):
    class DataOut(Event):
        def __init__(self, data: str) -> None:
            super().__init__()
            self.data = data

    class DataIn(Event):
        def __init__(self, data: str) -> None:
            super().__init__()
            self.data = data

    class MessageRead(Event):
        def __init__(self, msg: str) -> None:
            super().__init__()
            self.msg = msg

    BORDER_TITLE: str = "Device"

    is_busy_reading = reactive(False)
    timeout: int = 2
    timeout_timer: Timer | None = None

    def compose(self) -> ComposeResult:
        with Vertical(id="container"):
            yield Input(id="output")
            with Horizontal():
                yield Input(id="write-termchars")
                yield Button("Write", id="write-button", variant="primary")
            yield RichLog(id="log", markup=True)
            yield Buffer(id="input-buffer")
            with Horizontal():
                yield Input(
                    placeholder="Type termination characters here...",
                    id="read-termchars",
                )
                yield Input(
                    value=str(self.timeout),
                    id="timeout",
                    restrict="[0-9]*",
                    validators=Integer(minimum=0),
                )
                yield Button("Read", id="read-button", variant="primary")

    def on_mount(self) -> None:
        self.query_one("#write-termchars").border_title = "Write Termination Characters"
        self.query_one("#log").border_title = "Application Log"
        self.query_one("#input-buffer").border_title = "Input Buffer"
        self.query_one("#read-termchars").border_title = "Read Termination Characters"
        self.query_one("#timeout").border_title = "Timeout"

    def watch_is_busy_reading(self, is_busy_read: bool) -> None:
        def unlock_read():
            self.is_busy_reading = False
            print(20 * "*" + "TRING")

        if is_busy_read:
            output: Input = self.query_one("#output")
            output.disabled = True
            output.placeholder = "Busy reading..."
            output.add_class("busy")
            self.query_one("#read-button").disabled = True
            self.query_one("#read-termchars").disabled = True
            self.query_one("#timeout").disabled = True
            self.timeout_timer = self.set_timer(
                delay=self.timeout, callback=unlock_read
            )
        else:
            output: Input = self.query_one("#output")
            output.disabled = False
            output.placeholder = "Type here to send data"
            output.remove_class("busy")
            self.query_one("#read-button").disabled = False
            self.query_one("#read-termchars").disabled = False
            self.query_one("#timeout").disabled = False
            if self.timeout_timer:
                self.timeout_timer.stop()

    @on(Input.Submitted, "#timeout")
    @on(DescendantBlur, "#timeout")
    def set_timeout(self) -> None:
        widget: Input
        if not (widget := self.query_one("#timeout")).is_valid:
            widget.value = "0"
        self.timeout = int(widget.value)

    @on(Input.Submitted)
    @on(Button.Pressed, "#write-button")
    def write(self) -> None:
        termchars: Input = self.query_one("#write-termchars").value
        output: Input = self.query_one("#output")
        self.post_message(self.DataOut(output.value + termchars))
        output.clear()

    @on(Button.Pressed, "#read-button")
    def read(self) -> None:
        termchars: Input = self.query_one("#read-termchars").value
        msg = self.query_one("#input-buffer").read(termchars=termchars)
        if msg is not None:
            self.post_message(self.MessageRead(msg))
        else:
            self.is_busy_reading = True

    @on(MessageRead)
    def log_read(self, event: MessageRead) -> None:
        self.query_one("#log").write(f'[dark_olive_green1]> Read ← "{event.msg}"')

    @on(DataOut)
    def log_write(self, event: DataOut) -> None:
        self.query_one("#log").write(f'[light_steel_blue1]> Write → "{event.data}"')
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
