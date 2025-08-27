from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Label, Digits
from textual.containers import Container, Horizontal, VerticalGroup, HorizontalGroup

def pad_text(text: str, pad_len: int, pad_char: str) -> str:
    if len(text) <= pad_len:
        new_text = text + (pad_char * (pad_len - len(text)))
    else:
        new_text = text[0:pad_len]

    return new_text

class CompanyInfo(Container):
    """Container for holding Company invoice totals"""
    def __init__(self, company: str="no-name"):
        self.company = company;

    def compose(self) -> ComposeResult:
        yield Label(self.company, classes="coinfoname")
        yield Digits("")
        

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
        yield Button("Date button", id="DateButton")
        yield Container("Trading Info", classes="co-info")
        yield Container("Tech Info", classes="co-info")
        yield Container("Investments Info", classes="co-info")
        yield Container("Holdco Info", classes="co-info")
    
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
        yield Button("Add Invoices", 
                     variant="warning",
                     classes="option", 
                     id="add")
        yield Button("View Invoices",
                     variant="warning",
                     classes="option",
                     id="view")
        yield Button("Export Data",
                     variant="warning", 
                     classes="option",
                     id="export")

class PayablesApp(App):
    "An app to manage accounts payable accross all OpCos."

    TITLE = "Accounts Payable by Patrick"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle appearance")
    ]
    CSS_PATH = "testpayables.tcss"

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