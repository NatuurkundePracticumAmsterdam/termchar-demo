from textual.reactive import reactive
from textual.widgets import Label


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
