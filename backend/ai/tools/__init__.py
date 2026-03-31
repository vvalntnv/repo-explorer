from __future__ import annotations

from pydantic_ai import Tool

from .ask_rag import ask_rag
from .glob import glob
from .list_files import list_files
from .read_file import read_file
from .search_code import search_code

READ_FILE_TOOL = Tool(read_file, takes_ctx=False)
LIST_FILES_TOOL = Tool(list_files, takes_ctx=False)
GLOB_TOOL = Tool(glob, takes_ctx=False)
SEARCH_CODE_TOOL = Tool(search_code, takes_ctx=False)
ASK_RAG_TOOL = Tool(ask_rag, takes_ctx=False)

ALL_TOOLS = [
    READ_FILE_TOOL,
    LIST_FILES_TOOL,
    GLOB_TOOL,
    SEARCH_CODE_TOOL,
    ASK_RAG_TOOL,
]

__all__ = [
    "ask_rag",
    "glob",
    "list_files",
    "read_file",
    "search_code",
    "READ_FILE_TOOL",
    "LIST_FILES_TOOL",
    "GLOB_TOOL",
    "SEARCH_CODE_TOOL",
    "ASK_RAG_TOOL",
    "ALL_TOOLS",
]
