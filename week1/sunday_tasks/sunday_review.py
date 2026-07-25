class TestResult:
    def __init__(self, name, passed, failed):
        self.name = name
        self.passed = passed
        self.failed = failed

    @property
    def pass_rate(self):
        total = self.passed + self.failed
        if total == 0:
            return 0
        return (self.passed / total) * 100

    @property
    def status(self):
        return "PASS" if self.pass_rate >= 80 else "FAIL"

    def __str__(self):
        return (
            f"Name: {self.name} | "
            f"Pass Rate: {self.pass_rate:.2f}% | "
            f"Status: {self.status}"
        )

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["name"],
            data["passed"],
            data["failed"]
        )

    @staticmethod
    def is_valid_name(name):
        return isinstance(name, str) and len(name.strip()) > 0


def analyse_results(results):
    if not results:
        return {
            "total": 0,
            "passing_suites": 0,
            "failing_suites": 0,
            "best": None,
            "worst": None
        }

    best = max(results, key=lambda r: r.pass_rate)
    worst = min(results, key=lambda r: r.pass_rate)

    return {
        "total": len(results),
        "passing_suites": sum(r.status == "PASS" for r in results),
        "failing_suites": sum(r.status == "FAIL" for r in results),
        "best": best.name,
        "worst": worst.name
    }


def find_duplicate_ids(ids):
    seen = set()
    duplicates = set()

    for id_ in ids:
        if id_ in seen:
            duplicates.add(id_)
        else:
            seen.add(id_)

    return duplicates



    ################################################################
# Part B — Write these 3 functions from memory right now (40 min)

# Open sunday_review.py. Without looking at any previous file, write these three things:

# Thing 1: A complete TestResult class that has:

# __init__ with name, passed, failed
# pass_rate as a @property
# status as a @property that returns "PASS" if pass_rate >= 80 else "FAIL"
# __str__ that shows name, pass_rate, and status
# A @classmethod called from_dict that creates a TestResult from a dict with keys "name", "passed", "failed"
# A @staticmethod called is_valid_name that returns True if name is a non-empty string

# Thing 2: A function called analyse_results that takes a list of TestResult objects and returns a dict with:

# "total": total number of results
# "passing_suites": count where status == "PASS"
# "failing_suites": count where status == "FAIL"
# "best": name of TestResult with highest pass_rate
# "worst": name of TestResult with lowest pass_rate

# Thing 3: Write find_duplicate_ids — the set-based implementation — completely from memory. No hints.