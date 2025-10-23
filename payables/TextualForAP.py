from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Input, Button, Log, Label
from textual.containers import VerticalGroup, HorizontalGroup
import pyodbc
import pandas as pd

import APDatabase


class LoginScreen(Screen):
    def compose(self) -> ComposeResult:
        yield VerticalGroup(
            Input(placeholder="Username", id="un"),
            Input(placeholder="Password", password=True, id="pw"),
            Button(label="Log in", variant="primary", id="login"),
            id="loginscreen",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        id = event.button.id
        if id == "login":
            un = self.query_one(selector="#un").value
            pw = self.query_one(selector="#pw").value
            conn = APDatabase.establish_db_connection(uid=un, pwd=pw)
            self.dismiss(conn)


class HomeScreen(Screen):
    def compose(self) -> ComposeResult:
        yield HorizontalGroup(
            VerticalGroup(
                Label("Trading", id="tradingtag"),
                Label("Technologies", id="techtag"),
                Label("Holdco", id="holdcotag"),
                Label("Investments", id="investag"),
                id="summary",
            ),
            VerticalGroup(
                Button("Add invoices", id="add_invoices"),
                Button("View/Edit invoices", id="view_edit"),
                Button("Add Vendor", id="add_vendor"),
                Button("Create Payment Files", id="pmt_files"),
                Button("Create JE Files", id="create_jes"),
                Button("Exit", variant="error"),
                id="options",
            ),
        )


class AccountsPayableApp(App):
    """A Textual app for managing accounts payable."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    SCREENS = {"login": LoginScreen, "home": HomeScreen}
    CSS_PATH = "AP.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        self.push_screen("login", self.receive_conn)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""

        self.theme = (
            "textual-dark"
            if self.theme == "textual-light"
            else "textual-light"
        )

    def receive_conn(self, connection: pyodbc.Connection) -> None:
        self.conn = connection
        self.push_screen("home")


if __name__ == "__main__":
    app = AccountsPayableApp()
    app.run()
