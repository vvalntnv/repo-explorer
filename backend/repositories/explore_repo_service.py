import asyncio
from pathlib import Path

from vectors import embedder


class ExploreRepositoryService:
    def __init__(
        self,
        path: str,
        simultanious_file_exploraton_batch_size: int = 100,
    ) -> None:
        self.path = path
        self.simultanious_file_exploraton_batch_size = (
            simultanious_file_exploraton_batch_size
        )

    async def explore(self) -> list[Path]:
        directory_path = await self._assert_directory_exists()
        await self._assert_in_git_repo(directory_path)
        files = await self._get_files(directory_path)

        await self._explore_file_structure(files)

        return files

    async def _explore_file_structure(self, files: list[Path]) -> None:
        total_batches = (len(files) // self.simultanious_file_exploraton_batch_size) + 1

        for batch_number in range(0, total_batches):
            start = batch_number * self.simultanious_file_exploraton_batch_size
            end = start + self.simultanious_file_exploraton_batch_size

            batch = files[start:end]

            async with asyncio.TaskGroup() as tg:
                tasks: list[asyncio.Task] = []
                for file in batch:
                    task = tg.create_task(embedder.embed_file(file))
                    tasks.append(task)

                for task in tasks:
                    task.result()

    async def _get_files(self, directory_path: Path) -> list[Path]:
        process = await asyncio.create_subprocess_exec(
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            cwd=directory_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"Failed to list files for path '{directory_path}'")

        files = [
            (directory_path / line).resolve()
            for line in stdout.decode().splitlines()
            if line.strip()
        ]
        return files

    async def _assert_directory_exists(self) -> Path:
        directory_path = Path(self.path).expanduser().resolve()

        if not directory_path.exists():
            raise RuntimeError(f"Path '{directory_path}' does not exist")

        if not directory_path.is_dir():
            raise RuntimeError(f"Path '{directory_path}' is not a directory")

        return directory_path

    async def _assert_in_git_repo(self, directory_path: Path) -> None:
        process = await asyncio.create_subprocess_exec(
            "git",
            "rev-parse",
            "--is-inside-work-tree",
            cwd=directory_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, _ = await process.communicate()
        is_repo = process.returncode == 0 and stdout.decode().strip() == "true"
        if is_repo:
            return

        raise RuntimeError(f"Path '{directory_path}' is not inside a git repository")
