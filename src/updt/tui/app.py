"""Textual TUI application for updt."""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Static

from ..models.update import UpdateInfo


class UpdtTUI(App):
    """A Textual TUI for managing package updates."""

    CSS = """
    Screen {
        background: $surface;
    }

    #title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
        padding: 1;
    }

    #status {
        width: 100%;
        content-align: center middle;
        padding: 1;
        color: $text-muted;
    }

    .button-container {
        width: 100%;
        height: auto;
        align: center middle;
        padding: 1;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "check", "Check Updates"),
        ("u", "update", "Update All"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        """Initialize the TUI."""
        super().__init__(*args, **kwargs)
        self.updates: list[UpdateInfo] = []

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Container(
            Static("🔄 Universal Package Dependency Tracker", id="title"),
            Static("Press 'c' to check for updates", id="status"),
            Vertical(
                Button("Check Updates", id="check-btn", variant="primary"),
                Button("Update All", id="update-btn", variant="success"),
                Button("Refresh", id="refresh-btn"),
                classes="button-container",
            ),
            DataTable(),
        )
        yield Footer()

    def on_mount(self) -> None:
        """Set up the data table when mounted."""
        table = self.query_one(DataTable)
        table.add_columns("Ecosystem", "Package", "Current", "Latest", "Type")
        table.cursor_type = "row"

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "check-btn":
            await self.action_check()
        elif event.button.id == "update-btn":
            await self.action_update()
        elif event.button.id == "refresh-btn":
            await self.action_refresh()

    async def action_check(self) -> None:
        """Check for updates."""
        status = self.query_one("#status", Static)
        status.update("Checking for updates...")
        # TODO: Implement actual update checking
        # This would integrate with UpdateManager
        await self.action_refresh()
        status.update(f"Found {len(self.updates)} updates")

    async def action_update(self) -> None:
        """Perform updates."""
        status = self.query_one("#status", Static)
        status.update("Updating packages...")
        # TODO: Implement actual updates
        # This would integrate with UpdateManager
        status.update("Updates complete!")

    async def action_refresh(self) -> None:
        """Refresh the display."""
        table = self.query_one(DataTable)
        table.clear()
        for update in self.updates:
            table.add_row(
                update.ecosystem,
                update.package,
                update.current_version or "N/A",
                update.latest_version or "N/A",
                "Global" if update.is_global else "Project",
            )


def run_tui() -> None:
    """Run the TUI application."""
    app = UpdtTUI()
    app.run()
