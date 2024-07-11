from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, TabbedContent

from termchar_demo.advanced_demo import AdvancedDemo
from termchar_demo.basic_demo import BasicDemo


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
