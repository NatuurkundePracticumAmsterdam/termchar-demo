from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label


class Arrows(Container):
    def compose(self) -> ComposeResult:
        stem_length = int(self.styles.width.value) - 1
        yield Label(stem_length * "─" + "▶", id="right")
        yield Label("◀" + stem_length * "─", id="left")
