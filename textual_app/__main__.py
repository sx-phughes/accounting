from textual.app import App, ComposeResult
from textual.events import Key
from textual.widgets import Welcome, Button, Label, Header

class MyApp(App):
    TITLE = "A Question App"
    SUB_TITLE = "whoooo meee??"
    def compose (self) -> ComposeResult:
        yield Header()
        yield Label("Do you love Textual?", id="question")
        yield Button("Yes", id="yes", variant="primary")
        yield Button("No", id="no", variant="error")

    def on_mount(self) -> None:
        self.screen.styles.background = "darkblue"
    
    def on_key(self, event: Key):
        self.title = event.key
        self.sub_title = f"You just pressed {event.key}!"

if __name__ == "__main__":
    app = MyApp()
    app.run()