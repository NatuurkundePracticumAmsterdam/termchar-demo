from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Input, Label, RichLog


class Client(Container):
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Input(placeholder="Send characters", id="output")
            yield RichLog()
            yield (label := Label(id="input-buffer"))
            label.border_title = "Input Buffer"


class Server(Container):
    def compose(self) -> ComposeResult:
        with Vertical():
            yield (label := Label(id="input-buffer"))
            label.border_title = "Input Buffer"
            yield RichLog()
            yield Input(placeholder="Send characters", id="output")


class TermCharDemo(App[None]):
    CSS_PATH = "app.tcss"

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Client()
            yield Server()


TermCharDemo().run()
