from datetime import datetime
from pathlib import Path

TIME_FORMAT = "%d.%m.%Y %H:%M:%S"
REPORT_PATH = Path(__file__).with_name("report.txt")


class SessionReport:
    HEADER = (
        "+------------------------------------+\n"
        "| login | time_in | time_out |\n"
        "|---------|------------|-------------|\n"
    )

    def __init__(self, login):
        self._login = login
        self._time_in = SessionReport.now()

    @staticmethod
    def now():
        return datetime.now().strftime(TIME_FORMAT)

    def save(self, path=REPORT_PATH):
        is_new = not path.exists() or path.stat().st_size == 0
        row = "|%s | %s | %s |\n" % (self._login, self._time_in, SessionReport.now())
        with open(path, "a", encoding="utf-8") as f:
            if is_new:
                f.write(SessionReport.HEADER)
            f.write(row)
