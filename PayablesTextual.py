from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Label
from textual.containers import Container, Horizontal, VerticalGroup, HorizontalGroup

def pad_text(text: str, pad_len: int, pad_char: str) -> str:
    if len(text) <= pad_len:
        new_text = text + (pad_char * (pad_len - len(text)))
    else:
        new_text = text[0:pad_len]

    return new_text


class CompanyTotal(HorizontalGroup):
    def __init__(self, company_name: str, total_amount: int=0) -> None:
        self.co_name = company_name
        self.amount = total_amount

    def compose(self) -> ComposeResult:
        yield Label(self.co_name, id=self.co_name)
        yield Label(f"${self.amount:,.2f}", id=self.co_name + "total")

    def watch_amount(self) -> None:
        self.query_one(f"#{self.co_name}total").label = self.amount
        
class SummaryPanel(VerticalGroup):
    "A summary panel of the current payables workbook."

    company_amounts = {
        "Trading": 0,
        "Tech": 0,
        "Investments": 0,
        "Holdco": 0
    }
    def on_mount(self) -> None:
        for co in self.company_amounts.keys():
            self.company_amounts[co] = 0

    def compose(self) -> ComposeResult:
        total_widgets = []
        for co in self.company_amounts.keys():
            amt = self.company_amounts[co]
            new_widget = CompanyTotal(co, amt)
            total_widgets.append(new_widget)
        yield Button("2025-08-31", "default")
        yield VerticalGroup(*total_widgets)
        # yield Label(self.construct_content(), id="cototals")
    
    def watch_company_amounts(self) -> None:
        self.query_one("#cototals").renderable = self.construct_content()
    
    def construct_company_string(self, company: str) -> str:
        info = pad_text(company, 15, " ")
        string_amount = f"${self.company_amounts[company]:,.2f}"
        info = ": ".join([info, string_amount])
        return info
    
    def construct_content(self) -> str:
        result = ""
        for co in self.company_amounts.keys():
            co_info = self.construct_company_string(co)
            result = "\n".join([result, co_info])
        return result
            
class OptionsPanel(VerticalGroup):
    """A panel for accounts payable options."""

    def compose(self) -> ComposeResult:
        yield Button("Add Invoices", variant="warning", id="add")
        yield Button("View Invoices", variant="warning", id="view")
        yield Button("Export Data", variant="warning", id="export")

class PayablesApp(App):
    "An app to manage accounts payable accross all OpCos."

    TITLE = "Accounts Payable by Patrick"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle appearance")
    ]
    CSS_PATH = "payables.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            SummaryPanel(),
            OptionsPanel()
        )
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


if __name__ == "__main__":
    app = PayablesApp()
    app.run()