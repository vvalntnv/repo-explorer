from functools import partial
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Button, Footer, Header, Input, Static

from frontend.components.repo_chooser import RepoChooserScreen
from frontend.components.text_area import InputArea


class ChatApplication(App):
    CSS_PATH = "styles/main.tcss"
    BINDINGS = [
        ("i", "enter_insert_mode", "Enter insert mode"),
        ("r", "open_repo_chooser", "Choose repository"),
        ("ctrl+c", "clear_input", "Clear input"),
        ("escape", "exit_insert_mode", "Exit insert mode"),
        ("q", "quit_app", "Quit app"),
    ]

    selected_repo: Path | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="app-shell"):
            with Vertical(id="panel"):
                yield Static("Repo Explorer", id="title")
                yield Static(
                    "Normal: i insert, r repo, q quit. Insert: Ctrl+C clear, Esc normal.",
                    id="subtitle",
                )
                yield Static("Repository: not selected", id="repo-status")
                yield InputArea(id="input-area")
        yield Footer()

    def on_mount(self) -> None:
        input_area = self.query_one(InputArea)
        input_area.set_locked(True)
        input_area.set_insert_mode(False)

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        input_area = self.query_one(InputArea)

        if action == "exit_insert_mode":
            return input_area.insert_mode

        if action == "open_repo_chooser":
            return not input_area.insert_mode

        if action == "clear_input":
            return input_area.insert_mode and not input_area.locked

        if not input_area.insert_mode:
            return True

        if action in self._simple_key_actions():
            return False

        return True

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "message-input":
            self._show_enter_hit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send-btn":
            self._show_enter_hit()

    def action_enter_insert_mode(self) -> None:
        input_area = self.query_one(InputArea)
        if input_area.locked:
            self._open_repo_chooser(enter_insert_after_select=True)
            return

        input_area.set_insert_mode(True)

    def action_open_repo_chooser(self) -> None:
        self._open_repo_chooser(enter_insert_after_select=False)

    def action_exit_insert_mode(self) -> None:
        self.query_one(InputArea).set_insert_mode(False)

    def action_clear_input(self) -> None:
        self.query_one("#message-input", Input).clear()
        self.query_one(InputArea).set_status("Input cleared")

    def action_quit_app(self) -> None:
        self.exit()

    def _show_enter_hit(self) -> None:
        input_area = self.query_one(InputArea)
        input_area.set_status("Enter is hit")
        self.query_one("#message-input", Input).clear()

    def _open_repo_chooser(self, enter_insert_after_select: bool) -> None:
        start_path = self.selected_repo or Path.cwd()
        callback = partial(self._handle_repo_selected, enter_insert_after_select)
        self.push_screen(RepoChooserScreen(start_path=start_path), callback)

    def _handle_repo_selected(
        self, enter_insert_after_select: bool, repo_path: Path | None
    ) -> None:
        if repo_path is None:
            return

        self.selected_repo = repo_path
        self.query_one("#repo-status", Static).update(f"Repository: {repo_path}")

        input_area = self.query_one(InputArea)
        input_area.set_locked(False)
        input_area.set_status("Repository selected. Press Enter to test input.")
        input_area.set_insert_mode(enter_insert_after_select)

    @classmethod
    def _simple_key_actions(cls) -> set[str]:
        simple_actions: set[str] = set()

        for keys, action, _description in cls.BINDINGS:
            key_list = [key.strip() for key in keys.split(",")]
            if any("+" not in key for key in key_list):
                simple_actions.add(action)

        simple_actions.discard("exit_insert_mode")
        return simple_actions
