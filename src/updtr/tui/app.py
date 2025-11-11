"""Textual TUI application for updtr."""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Static

from ..models.config import UpdtConfig
from ..models.update import UpdateInfo
from ..updater import UpdateManager


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

    DataTable {
        height: 1fr;
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
        self.config = UpdtConfig()
        self.manager: UpdateManager | None = None

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
            DataTable(id="updates-table"),
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
        status.update("Initializing plugins...")

        # Initialize manager if not already done
        if not self.manager:
            self.manager = UpdateManager(self.config)
            await self.manager.initialize()

        status.update("Checking for updates...")
        self.updates = await self.manager.check_all_updates()

        await self.action_refresh()

        if self.updates:
            status.update(f"Found {len(self.updates)} updates")
        else:
            status.update("All packages are up to date!")

    async def action_update(self) -> None:
        """Perform updates."""
        if not self.updates:
            status = self.query_one("#status", Static)
            status.update("No updates available. Check for updates first.")
            return

        status = self.query_one("#status", Static)
        status.update(f"Updating {len(self.updates)} packages...")

        if not self.manager:
            self.manager = UpdateManager(self.config)
            await self.manager.initialize()

        results = await self.manager.perform_updates(self.updates, dry_run=False)

        success_count = sum(1 for r in results if r.status.value == "success")
        status.update(f"Updated {success_count} of {len(self.updates)} packages")

        # Clear updates after performing them
        self.updates = []
        await self.action_refresh()

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
