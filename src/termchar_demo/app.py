import importlib.resources

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Markdown, TabbedContent, TabPane

from termchar_demo.advanced_demo import AdvancedDemo
from termchar_demo.basic_demo import BasicDemo


class TermCharDemo(App[None]):
    CSS_PATH = "app.tcss"

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with TabbedContent():
            with TabPane("Introduction", id="intro"):
                yield Markdown(
                    (
                        importlib.resources.files("termchar_demo") / "intro.md"
                    ).read_text()
                )
            with TabPane("Basic", id="basic"):
                yield BasicDemo()
            with TabPane("Advanced", id="advanced"):
                yield AdvancedDemo()
            with TabPane("Background", id="background"):
                yield Markdown(
                    (
                        importlib.resources.files("termchar_demo") / "background.md"
                    ).read_text()
                )

    @on(Markdown.LinkClicked)
    def open_web_link(self, event: Markdown.LinkClicked) -> None:
        self.open_url(event.href)

    def action_intro(self) -> None:
        self.query_one(TabbedContent).active = "intro"

    def action_basic(self) -> None:
        self.query_one(TabbedContent).active = "basic"

    def action_advanced(self) -> None:
        self.query_one(TabbedContent).active = "advanced"


def main():
    TermCharDemo().run()


app = TermCharDemo
if __name__ == "__main__":
    main()
