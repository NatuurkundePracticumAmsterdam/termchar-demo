from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.events import DescendantBlur, Event, Mount
from textual.reactive import reactive
from textual.timer import Timer
from textual.validation import Integer
from textual.widgets import Button, Input, RichLog

from termchar_demo.buffer import Buffer


class Device(Container):
    class DataOut(Event):
        def __init__(self, data: str, sender: "Device") -> None:
            super().__init__()
            self.data = data
            self.sender = sender

    class DataIn(Event):
        def __init__(self, data: str) -> None:
            super().__init__()
            self.data = data

    class MessageRead(Event):
        def __init__(self, msg: str) -> None:
            super().__init__()
            self.msg = msg

    BINDINGS = [("ctrl+o", "focus_message", "Focus message")]

    BORDER_TITLE: str = "Device"
    TIMEOUT = 2

    is_busy_reading = reactive(False)
    timeout: int
    timeout_timer: Timer | None = None

    def output_widgets(self) -> ComposeResult:
        yield Input(id="output")
        with Horizontal():
            yield Input(id="write-termchars")
            yield Button("Write", id="write-button", variant="primary")

    def input_widgets(self) -> ComposeResult:
        with Horizontal():
            yield Buffer(id="input-buffer", length=30)
            yield Button("Clear", id="clear-button", variant="primary")
        with Horizontal():
            yield Input(
                placeholder="Type termination characters here...",
                id="read-termchars",
            )
            yield Input(
                value=str(self.TIMEOUT),
                id="timeout",
                restrict="[0-9]*",
                validators=Integer(minimum=0),
            )
            yield Button("Read", id="read-button", variant="primary")

    def log_widget(self) -> ComposeResult:
        yield RichLog(id="log", markup=True)

    def compose(self) -> ComposeResult:
        with Vertical(id="container"):
            yield from self.output_widgets()
            yield from self.log_widget()
            yield from self.input_widgets()

    def on_mount(self) -> None:
        self.query_one("#write-termchars").border_title = "Write Termination Characters"
        self.query_one("#log").border_title = "Application Log"
        self.query_one("#input-buffer").border_title = "Input Buffer"
        self.query_one("#read-termchars").border_title = "Read Termination Characters"
        self.query_one("#timeout").border_title = "Timeout"
        self.timeout = self.TIMEOUT

    def watch_is_busy_reading(self, is_busy_read: bool) -> None:
        def unlock_read():
            self.is_busy_reading = False

        if is_busy_read:
            output: Input = self.query_one("#output")
            output.disabled = True
            output.placeholder = "Waiting for message..."
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

    @on(Input.Submitted, "#output")
    @on(Input.Submitted, "#write-termchars")
    @on(Button.Pressed, "#write-button")
    def write(self) -> None:
        termchars: Input = self.query_one("#write-termchars").value
        output: Input = self.query_one("#output")
        self.post_message(self.DataOut(output.value + termchars, sender=self))
        output.clear()

    @on(Input.Changed, "#read-termchars")
    def update_input_buffer(self, event: Input.Changed) -> None:
        self.query_one("#input-buffer").termchars = event.input.value

    @on(Input.Submitted, "#read-termchars")
    @on(Button.Pressed, "#read-button")
    def perform_read(self) -> None:
        self.read()

    def read(self) -> None:
        termchars: Input = self.query_one("#read-termchars").value
        msg = self.query_one("#input-buffer").read(termchars=termchars)
        if msg is not None:
            self.post_message(self.MessageRead(msg))
            self.is_busy_reading = False
        else:
            self.is_busy_reading = True

    @on(Button.Pressed, "#clear-button")
    def clear_buffer(self) -> None:
        self.query_one("#input-buffer").clear()

    @on(MessageRead)
    def log_read(self, event: MessageRead) -> None:
        self.query_one("#log").write(f'[dark_olive_green1]> Read ← "{event.msg}"')

    @on(DataOut)
    def log_write(self, event: DataOut) -> None:
        msg = event.data.removesuffix(self.query_one("#write-termchars").value)
        self.query_one("#log").write(f'[light_steel_blue1]> Write → "{msg}"')

    @on(DataIn)
    def fill_buffer(self, event: DataIn) -> None:
        buffer: Buffer = self.query_one("#input-buffer")
        buffer.append(event.data)
        if self.is_busy_reading:
            self.read()

    def action_focus_message(self) -> None:
        self.query_one("#output").focus()


class SimpleDevice(Device):
    TIMEOUT = 0

    def input_widgets(self) -> ComposeResult:
        with Horizontal():
            yield Buffer(id="input-buffer")
            yield Button("Clear", id="clear-button", variant="primary")
        with Horizontal():
            yield Input(
                placeholder="Type termination characters here...",
                id="read-termchars",
            )
            yield Button("Read", id="read-button", variant="primary")

    def compose(self) -> ComposeResult:
        with Vertical(id="container"):
            yield from self.output_widgets()
            yield from self.log_widget()
            yield from self.input_widgets()

    @on(Mount)
    def on_mount(self, event: Mount) -> None:
        event.prevent_default()
        self.query_one("#write-termchars").border_title = "Write Termination Characters"
        self.query_one("#log").border_title = "Application Log"
        self.query_one("#input-buffer").border_title = "Input"
        self.query_one("#read-termchars").border_title = "Read Termination Characters"

    def watch_is_busy_reading(self, is_busy_read: bool) -> None:
        if is_busy_read:
            output: Input = self.query_one("#output")
            output.disabled = True
            output.placeholder = "Sending auto-replies..."
            output.add_class("busy")
            self.query_one("#read-button").disabled = True
            self.query_one("#read-termchars").disabled = True
        else:
            output: Input = self.query_one("#output")
            output.disabled = False
            output.placeholder = "Type here to send data"
            output.remove_class("busy")
            self.query_one("#read-button").disabled = False
            self.query_one("#read-termchars").disabled = False
