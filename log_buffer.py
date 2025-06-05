class LogBuffer:
    """Simple FIFO buffer for log entries."""

    def __init__(self, max_entries: int = 1000) -> None:
        self.max_entries = max_entries
        self.entries: list[str] = []

    def append(self, entry: str) -> None:
        """Add *entry* and truncate old records if needed."""
        self.entries.append(entry)
        if len(self.entries) > self.max_entries:
            excess = len(self.entries) - self.max_entries
            self.entries = self.entries[excess:]

    def extend(self, entries: list[str]) -> None:
        for e in entries:
            self.append(e)

    def render_html(self, sep: str = "<br>") -> str:
        """Return entries joined with ``sep`` for display."""
        return sep.join(self.entries)
