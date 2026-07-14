"""Small dependency-free Value Change Dump (VCD) writer."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TextIO


@dataclass(frozen=True)
class VcdSignal:
    scope: tuple[str, ...]
    name: str
    width: int
    identifier: str


class _Scope:
    def __init__(self) -> None:
        self.signals: list[VcdSignal] = []
        self.children: dict[str, "_Scope"] = {}


class VcdWriter:
    """Write integer and boolean signals to a standard VCD file."""

    def __init__(self, path: str | Path, timescale: str = "1 ns") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._file: TextIO = self.path.open("w", encoding="utf-8", newline="\n")
        self._timescale = timescale
        self._signals: list[VcdSignal] = []
        self._last_values: dict[str, int] = {}
        self._started = False
        self._closed = False
        self._time = -1

    def register(
        self,
        scope: str | tuple[str, ...],
        name: str,
        width: int = 1,
    ) -> VcdSignal:
        if self._started:
            raise RuntimeError("VCD signals must be registered before start()")
        if width < 1:
            raise ValueError("VCD signal width must be positive")

        scope_parts = (scope,) if isinstance(scope, str) else tuple(scope)
        if not scope_parts:
            raise ValueError("VCD signal must belong to a scope")

        signal = VcdSignal(
            scope=scope_parts,
            name=name,
            width=width,
            identifier=f"s{len(self._signals)}",
        )
        self._signals.append(signal)
        return signal

    def start(self) -> None:
        if self._started:
            return

        self._file.write("$date\n")
        self._file.write(f"  {datetime.now().isoformat(timespec='seconds')}\n")
        self._file.write("$end\n")
        self._file.write("$version\n  RISC-V Python VCD tracer\n$end\n")
        self._file.write(f"$timescale {self._timescale} $end\n")

        root = _Scope()
        for signal in self._signals:
            node = root
            for scope_name in signal.scope:
                node = node.children.setdefault(scope_name, _Scope())
            node.signals.append(signal)

        self._write_scope(root)
        self._file.write("$enddefinitions $end\n")
        self._started = True

    def _write_scope(self, node: _Scope) -> None:
        for scope_name, child in node.children.items():
            self._file.write(f"$scope module {scope_name} $end\n")
            for signal in child.signals:
                suffix = "" if signal.width == 1 else f" [{signal.width - 1}:0]"
                self._file.write(
                    f"$var wire {signal.width} {signal.identifier} "
                    f"{signal.name}{suffix} $end\n"
                )
            self._write_scope(child)
            self._file.write("$upscope $end\n")

    def set_time(self, timestamp: int) -> None:
        if not self._started:
            raise RuntimeError("start() must be called before writing values")
        if timestamp < self._time:
            raise ValueError("VCD timestamps must be monotonic")
        if timestamp != self._time:
            self._file.write(f"#{timestamp}\n")
            self._time = timestamp

    def change(
        self,
        signal: VcdSignal,
        value: int | bool,
        *,
        force: bool = False,
    ) -> None:
        if not self._started:
            raise RuntimeError("start() must be called before writing values")

        masked = int(value) & ((1 << signal.width) - 1)
        if not force and self._last_values.get(signal.identifier) == masked:
            return

        if signal.width == 1:
            self._file.write(f"{masked}{signal.identifier}\n")
        else:
            self._file.write(f"b{masked:0{signal.width}b} {signal.identifier}\n")
        self._last_values[signal.identifier] = masked

    def close(self) -> None:
        if self._closed:
            return
        self._file.flush()
        self._file.close()
        self._closed = True

    def __enter__(self) -> "VcdWriter":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
