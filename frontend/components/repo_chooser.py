from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DirectoryTree, Static

from frontend.services.repo_validation import is_git_repository


class RepoChooserScreen(ModalScreen[Path | None]):
    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, start_path: Path | None = None) -> None:
        super().__init__()
        self.start_path = start_path or Path.cwd()
        self.selected_path: Path | None = None

    def compose(self) -> ComposeResult:
        with Container(id="repo-modal-shell"):
            with Vertical(id="repo-modal"):
                yield Static("Select Repository", id="repo-modal-title")
                yield Static(
                    "Choose a directory that contains a .git folder.",
                    id="repo-modal-subtitle",
                )
                yield Static(
                    "Use arrows to navigate, Space to expand, Enter to choose.",
                    id="repo-modal-help",
                )
                yield DirectoryTree(str(self.start_path), id="repo-tree")
                yield Static("Selected: none", id="repo-selected-path")
                yield Static("", id="repo-warning")
                with Horizontal(id="repo-actions"):
                    yield Button("Choose Repo", id="repo-confirm", variant="primary")
                    yield Button("Cancel", id="repo-cancel")

    def on_mount(self) -> None:
        self.query_one("#repo-tree", DirectoryTree).focus()

    def on_directory_tree_directory_selected(
        self, event: DirectoryTree.DirectorySelected
    ) -> None:
        self.selected_path = event.path
        self.query_one("#repo-selected-path", Static).update(f"Selected: {event.path}")
        self.query_one("#repo-warning", Static).update("")
        self._confirm_selection()

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        self.selected_path = None
        self.query_one("#repo-warning", Static).update(
            "Select a directory, not a file."
        )
        self.query_one("#repo-selected-path", Static).update(
            f"File highlighted: {event.path.name}"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "repo-cancel":
            self.dismiss(None)
            return

        if event.button.id == "repo-confirm":
            self._confirm_selection()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def _confirm_selection(self) -> None:
        warning = self.query_one("#repo-warning", Static)

        if self.selected_path is None:
            warning.update("Pick a directory before confirming.")
            return

        if not is_git_repository(self.selected_path):
            warning.update("LLM cannot analyze non-git repositories.")
            return

        self.dismiss(self.selected_path)
