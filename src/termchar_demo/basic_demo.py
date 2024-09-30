import asyncio
from random import choice

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Input

from termchar_demo.advanced_demo import AdvancedDemo, Client, Server
from termchar_demo.arrows import Arrows
from termchar_demo.devices import SimpleDevice

REPLIES = [
    "Got it, thanks!",
    "Received, thanks!",
    "Thanks, noted.",
    "Understood, thanks!",
    "Acknowledged.",
    "Thanks, will do.",
    "Got it.",
    "Noted.",
    "Copy that.",
    "Received.",
]


class BasicClient(Client, SimpleDevice):
    @on(Client.DataOut)
    def disable_inputs(self) -> None:
        self.query_one("#output").disabled = True
        # self.query_one("#write-termchars").disabled = True


class BasicServer(Server, SimpleDevice):
    BORDER_TITLE: str = "Server"
    TIMEOUT = 0

    def on_mount(self) -> None:
        (widget := self.query_one("#read-termchars")).value = r"\n"
        widget.disabled = True
        (widget := self.query_one("#write-termchars")).value = r"\r\n"
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
                    choice(REPLIES) + termchars,
                    sender=self,
                )
            )


class BasicDemo(AdvancedDemo):
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield BasicClient()
            yield Arrows()
            yield BasicServer()

    @on(SimpleDevice.DataOut)
    def send_data(self, event: SimpleDevice.DataOut) -> None:
        event.prevent_default()
        if event.sender == self.query_one(Client):
            target = Server
            dataflow_target = "#right"
        else:
            target = Client
            dataflow_target = "#left"

        async def callback():
            arrow = self.query_one(dataflow_target).add_class("active")
            await asyncio.sleep(1)
            arrow.remove_class("active")
            self.query_one(target).post_message(SimpleDevice.DataIn(event.data))

        self.call_later(callback)
