import asyncio
from random import choice

from textual import on, work
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

DELAY = 1.0


class BasicClient(Client, SimpleDevice):
    @on(Client.DataOut)
    def focus_write_button(self) -> None:
        self.query_one("#write-button").focus()

    def read(self) -> None:
        super().read()
        self.is_busy_reading = False


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
        self.myworker()

    @work
    async def myworker(self):
        await asyncio.sleep(DELAY)
        termchars: Input = self.query_one("#read-termchars").value
        msg = self.query_one("#input-buffer").read(termchars=termchars)
        if msg is not None:
            self.post_message(self.MessageRead(msg))
            await asyncio.sleep(DELAY)
            termchars: Input = self.query_one("#write-termchars").value
            self.post_message(
                self.DataOut(
                    choice(REPLIES) + termchars,
                    sender=self,
                )
            )
            await asyncio.sleep(DELAY)
            self.query_one("#output").add_class("active")
            await asyncio.sleep(DELAY)
            self.query_one("#output").remove_class("active")


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
        self.animate_send_data(event.data, target, dataflow_target)

    @work
    async def animate_send_data(
        self, data: str, data_target: SimpleDevice, dataflow_target: str
    ) -> None:
        await asyncio.sleep(DELAY)
        arrow = self.query_one(dataflow_target).add_class("active")
        await asyncio.sleep(DELAY)
        arrow.remove_class("active")
        self.query_one(data_target).post_message(SimpleDevice.DataIn(data))
