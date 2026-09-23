"""OpsPulse log parser — reads raw job logs into structured records."""


class LogRecord:
    """One parsed log line. Encapsulates a single job event."""

    def __init__(self, timestamp, job, status, code, message):
        self.timestamp = timestamp
        self.job = job
        self.status = status
        self.code = code
        self.message = message

    @property
    def is_failure(self):
        return self.status == "FAILED"

    def __repr__(self):
        return f"<{self.job} {self.status} {self.code}>"


def parse_line(line):
    """Turn one raw log line into a LogRecord, or None if malformed."""
    parts = [p.strip() for p in line.split("|")]
    if len(parts) != 5:
        return None
    timestamp = parts[0]
    fields = {}
    for item in parts[1:]:
        key, value = item.split("=", 1)
        fields[key] = value
    return LogRecord(
        timestamp=timestamp,
        job=fields.get("JOB"),
        status=fields.get("STATUS"),
        code=fields.get("CODE"),
        message=fields.get("MSG"),
    )


def read_logs(filepath):
    """Generator: yield one LogRecord per valid line, lazily."""
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = parse_line(line)
            if record is not None:
                yield record


if __name__ == "__main__":
    records = read_logs("sample_logs.txt")
    failures = [r for r in records if r.is_failure]
    print(f"Found {len(failures)} failures:")
    for r in failures:
        print(f"  {r.timestamp}  {r.job}  ->  {r.message}")