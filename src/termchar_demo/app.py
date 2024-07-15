import importlib.resources
import webbrowser

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Markdown, TabbedContent

from termchar_demo.advanced_demo import AdvancedDemo
from termchar_demo.basic_demo import BasicDemo


class TermCharDemo(App[None]):
    CSS_PATH = "app.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with TabbedContent("Introduction", "Basic", "Advanced"):
            yield Markdown(
                (importlib.resources.files("termchar_demo") / "intro.md").read_text()
            )
            yield BasicDemo()
            yield AdvancedDemo()

    @on(Markdown.LinkClicked)
    def open_web_link(self, event: Markdown.LinkClicked) -> None:
        webbrowser.open(event.href)


def main():
    TermCharDemo().run()


app = TermCharDemo
if __name__ == "__main__":
    main()
