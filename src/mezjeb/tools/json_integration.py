import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict


class JsonIntegration:
    async def execute_import(
        self,
        file_path: str,
        *,
        encoding: str = "utf-8",
        **kwargs,
    ) -> Dict[str, Any]:
        """Import a JSON file and return its contents."""
        if kwargs:
            raise TypeError(f"Unexpected options: {', '.join(kwargs)}")

        def _read() -> Dict[str, Any]:
            with Path(file_path).open("r", encoding=encoding) as f:
                return json.load(f)

        return await asyncio.to_thread(_read)
    
    async def execute_export(
        self,
        file_path: str,
        data: dict,
        *,
        encoding: str = "utf-8",
        indent: int | None = 2,
        ensure_ascii: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """Export a dictionary to a JSON file and return a summary of the write."""
        if kwargs:
            raise TypeError(f"Unexpected options: {', '.join(kwargs)}")

        def _write() -> Dict[str, Any]:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            # Write to a temp file in the same directory, then atomically replace.
            # This way a crash mid-write can't leave a half-written JSON file.
            fd, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding=encoding) as f:
                    json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
                os.replace(tmp_name, path)
            except BaseException:
                Path(tmp_name).unlink(missing_ok=True)
                raise

            return {"path": str(path), "bytes_written": path.stat().st_size}

        return await asyncio.to_thread(_write)
                
        