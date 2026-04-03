from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Input, Static


class InputArea(Static):
    locked: bool = True
    insert_mode: bool = False

    def compose(self) -> ComposeResult:
        yield Static("-- LOCKED -- Select a repository", id="mode-indicator")
        with Horizontal(id="input-row"):
            yield Input(placeholder="Type a message", id="message-input")
            yield Button("Send", id="send-btn", variant="primary")
        yield Static("Pick a git repository to unlock input.", id="status")

    def on_mount(self) -> None:
        self.set_locked(True)

    def set_status(self, message: str) -> None:
        self.query_one("#status", Static).update(message)

    def set_locked(self, locked: bool) -> None:
        self.locked = locked
        if locked:
            self.insert_mode = False
            self.set_status("Pick a git repository to unlock input.")
        self._refresh_mode_indicator()
        self._sync_controls()

    def set_insert_mode(self, enabled: bool) -> None:
        if self.locked:
            self.insert_mode = False
            self._refresh_mode_indicator()
            self._sync_controls()
            return

        self.insert_mode = enabled
        self._refresh_mode_indicator()
        self._sync_controls()

    def _refresh_mode_indicator(self) -> None:
        mode_indicator = self.query_one("#mode-indicator", Static)
        mode_indicator.remove_class("locked")
        mode_indicator.remove_class("normal")
        mode_indicator.remove_class("insert")

        if self.locked:
            mode_indicator.update("-- LOCKED -- Press i or r to choose repository")
            mode_indicator.add_class("locked")
            return

        if self.insert_mode:
            mode_indicator.update("-- INSERT -- Press Esc to leave insert mode")
            mode_indicator.add_class("insert")
            return

        mode_indicator.update("-- NORMAL -- Press i to enter insert mode")
        mode_indicator.add_class("normal")

    def _sync_controls(self) -> None:
        message_input = self.query_one("#message-input", Input)
        send_button = self.query_one("#send-btn", Button)
        active_input = self.insert_mode and not self.locked

        message_input.disabled = not active_input
        send_button.disabled = not active_input

        if active_input:
            message_input.focus()
            return

        message_input.blur()
