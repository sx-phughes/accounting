from textual.app import App, ComposeResult
from textual.widgets import Welcome, Button

class MyApp(App):
    def on_key(self) -> None:
        self.mount(Welcome())
        self.query_one(Button).label = "Yes!"

    def on_mount(self) -> None:
        self.screen.styles.background = "darkblue"

if __name__ == "__main__":
    app = MyApp()
    app.run()