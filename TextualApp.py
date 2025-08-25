from time import monotonic

from textual.app import App, ComposeResult
from textual.events import Key
from textual.widgets import Button, Digits, Header, Footer
from textual.containers import HorizontalGroup, VerticalScroll
from textual.reactive import reactive

# class MyApp(App):
#     TITLE = "A Question App"
#     SUB_TITLE = "whoooo meee??"
#     def compose (self) -> ComposeResult:
#         yield Header()
#         yield Label("Do you love Textual?", id="question")
#         yield Button("Yes", id="yes", variant="primary")
#         yield Button("No", id="no", variant="error")

#     def on_mount(self) -> None:
#         self.screen.styles.background = "darkblue"
    
#     def on_key(self, event: Key):
#         self.title = event.key
#         self.sub_title = f"You just pressed {event.key}!"
class TimeDisplay(Digits):
    """A widget to display elapsed time."""
    start_time = reactive(monotonic)
    time = reactive(0.0) 
    total = reactive(0.0)

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.update_timer =  self.set_interval(
            1 / 60,
            self.update_time,
            pause=True
        )
    
    def update_time(self) -> None:
        """Method to update the time to the current time."""
        self.time = self.total + (monotonic() - self.start_time)
    
    def watch_time(self, time: float) -> None:
        """Called when the time attribute changes."""
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(time, 60)
        self.update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")
    
    def start(self) -> None:
        """Method to start (or resume) time updating."""
        self.start_time = monotonic()
        self.update_timer.resume()
        
    def stop(self) -> None:
        """Method to stop the time display updating."""
        self.update_timer.pause()
        self.total += monotonic() - self.start_time
        self.time = self.total
        
    def reset(self) -> None:
        """Method to reset the time display to zero."""
        self.total = 0
        self.time = 0

class Stopwatch(HorizontalGroup):
    """A stopwatch widget."""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        time_display = self.query_one(TimeDisplay)
        if button_id == "start":
            time_display.start()
            self.add_class("started")
        elif button_id == "stop":
            time_display.stop()
            self.remove_class("started")
        elif button_id == "reset":
            time_display.reset()

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        yield TimeDisplay()

class StopwatchApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "stopwatch.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("a", "add_stopwatch", "Add"),
        ("r", "remove_stopwatch", "Remove")
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield VerticalScroll(Stopwatch(), Stopwatch(), Stopwatch(), id="timers")
    
    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
    
    def action_add_stopwatch(self) -> None:
        """An action to add a timer."""
        new_stopwatch = Stopwatch()
        self.query_one("#timers").mount(new_stopwatch)
        new_stopwatch.scroll_visible()

    def action_remove_stopwatch(self) -> None:
        """An action to remove a timer."""
        timers = self.query("Stopwatch")
        if timers:
            timers.last().remove()

if __name__ == "__main__":
    app = StopwatchApp()
    app.run()