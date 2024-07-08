from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.events import DescendantBlur, Event, Mount
from textual.reactive import reactive
from textual.timer import Timer
from textual.validation import Integer
from textual.widgets import Button, Footer, Header, Input, Label, RichLog, TabbedContent


class Buffer(Label):
    data = reactive("")
    termchars = reactive("")

    def __init__(
        self,
        data: str = "",
        length: int | None = None,
        termchars: str = "",
        *args,
        **kwargs,
    ) -> None:
        super().__init__(data, *args, **kwargs)
        self.length = length
        if length is not None:
            self.styles.max_width = self.length + 2
        self.data = data
        self.termchars = termchars

    def render(self) -> str:
        if not self.termchars:
            return f"[bright_black]{self.data}[/]"
        elif self.termchars in self.data:
            messages = self.data.split(self.termchars)
            if (termchars := self.termchars).endswith("\\"):
                # a backslash just before a markup tag cancels that tag
                # escape the backslash
                termchars += "\\"
            data = (
                "[green]"
                + f"[/][dark_blue]{termchars}[/][green]".join(messages[:-1])
                + f"[/][dark_blue]{termchars}[/][orange1]{messages[-1]}[/]"
            )
        else:
            data = f"[orange1]{self.data}[/]"
        return data

    def append(self, new_data: str) -> None:
        self.data = (self.data + new_data)[: self.length]

    def clear(self) -> None:
        self.data = ""

    def watch_data(self):
        if self.length is not None:
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

    BORDER_TITLE: str = "Device"
    TIMEOUT = 2

    is_busy_reading = reactive(False)
    timeout: int
    timeout_timer: Timer | None = None

    def compose(self) -> ComposeResult:
        with Vertical(id="container"):
            yield Input(id="output")
            with Horizontal():
                yield Input(id="write-termchars")
                yield Button("Write", id="write-button", variant="primary")
            yield RichLog(id="log", markup=True)
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

    @on(Input.Submitted, "#output")
    @on(Button.Pressed, "#write-button")
    def write(self) -> None:
        termchars: Input = self.query_one("#write-termchars").value
        output: Input = self.query_one("#output")
        self.post_message(self.DataOut(output.value + termchars, sender=self))
        output.clear()

    @on(Input.Changed, "#read-termchars")
    def update_input_buffer(self, event: Input.Changed) -> None:
        self.query_one("#input-buffer").termchars = event.input.value

    @on(Button.Pressed, "#read-button")
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
        msg = event.data.rstrip(self.query_one("#write-termchars").value)
        self.query_one("#log").write(f'[light_steel_blue1]> Write → "{msg}"')

    @on(DataIn)
    def fill_buffer(self, event: DataIn) -> None:
        buffer: Buffer = self.query_one("#input-buffer")
        buffer.append(event.data)
        if self.is_busy_reading:
            self.read()


class SimpleDevice(Device):
    TIMEOUT = 0

    def compose(self) -> ComposeResult:
        with Vertical(id="container"):
            yield Input(id="output")
            with Horizontal():
                yield Input(id="write-termchars")
                yield Button("Write", id="write-button", variant="primary")
            yield RichLog(id="log", markup=True)
            with Horizontal():
                yield Buffer(id="input-buffer")
                yield Button("Clear", id="clear-button", variant="primary")
            with Horizontal():
                yield Input(
                    placeholder="Type termination characters here...",
                    id="read-termchars",
                )
                yield Button("Read", id="read-button", variant="primary")

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
            output.placeholder = "Busy reading..."
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


class Client(Device):
    BORDER_TITLE: str = "Client"


class Server(Device):
    BORDER_TITLE: str = "Server"
    TIMEOUT = 0

    def on_mount(self) -> None:
        self.query_one("#read-termchars").value = r"\n"
        self.query_one("#write-termchars").value = r"\n\r"


class BasicClient(Client, SimpleDevice): ...


class BasicServer(Server, SimpleDevice):
    BORDER_TITLE: str = "Server"
    TIMEOUT = 0

    def on_mount(self) -> None:
        (widget := self.query_one("#read-termchars")).value = r"\n"
        widget.disabled = True
        (widget := self.query_one("#write-termchars")).value = r"\n\r"
        widget.disabled = True
        self.query_one("#read-button").disabled = True
        self.query_one("#write-button").disabled = True
        self.is_busy_reading = True

    def read(self) -> None:
        termchars: Input = self.query_one("#read-termchars").value
        msg = self.query_one("#input-buffer").read(termchars=termchars)
        if msg is not None:
            self.post_message(self.MessageRead(msg))
            termchars: Input = self.query_one("#write-termchars").value
            self.post_message(
                self.DataOut(
                    f"Thank you, I got '{msg}'!" + termchars,
                    sender=self,
                )
            )


class AdvancedDemo(Container):
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Client()
            yield Server()

    @on(Device.DataOut)
    def send_data(self, event: Device.DataOut) -> None:
        if event.sender == self.query_one(Client):
            target = Server
        else:
            target = Client
        self.query_one(target).post_message(Device.DataIn(event.data))


class BasicDemo(AdvancedDemo):
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield BasicClient()
            yield BasicServer()


class TermCharDemo(App[None]):
    CSS_PATH = "app.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with TabbedContent("Basic Demo", "Advanced Demo"):
            yield BasicDemo()
            yield AdvancedDemo()


def main():
    TermCharDemo().run()


app = TermCharDemo
if __name__ == "__main__":
    main()
