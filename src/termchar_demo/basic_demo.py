from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Input

from termchar_demo.advanced_demo import AdvancedDemo, Client, Server
from termchar_demo.arrows import Arrows
from termchar_demo.devices import SimpleDevice


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
                    f"I got '{msg}'!" + termchars,
                    sender=self,
                )
            )


class BasicDemo(AdvancedDemo):
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield BasicClient()
            yield Arrows()
            yield BasicServer()
