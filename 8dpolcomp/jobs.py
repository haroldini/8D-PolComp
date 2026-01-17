
import sys
import json
import logging
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))


from application import create_app


# ---------- logging ----------
logger = logging.getLogger("jobs")
logger.setLevel(logging.INFO)

_handler = logging.StreamHandler(sys.stdout)
_handler.setLevel(logging.INFO)
_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s"))

if not logger.handlers:
    logger.addHandler(_handler)


# ---------- jobs ----------

def job_avg_identities(app):
    """
    Calculates and saves average axis values per identity.
    Intended schedule: monthly
    Output: application/data/demographics/axis_averages.json
    """
    
    from application.controllers.results import ResultsController as Results

    demo_path = PROJECT_ROOT / "application" / "data" / "demographics" / "demographics.json"
    avgs_path = PROJECT_ROOT / "application" / "data" / "demographics" / "axis_averages.json"

    logger.info("Loading demographics: %s", demo_path)

    with open(demo_path, "r", encoding="utf-8") as f:
        demographics = json.load(f)
        identities = list(demographics["identities"])
        identities.append("Average Result")

    logger.info("Calculating averages for %d identities...", len(identities))

    with app.app_context():
        avg_identities = Results.get_avg_identities(identities, min_results=50)

    logger.info("Writing averages: %s", avgs_path)

    with open(avgs_path, "w", encoding="utf-8") as f:
        json.dump(avg_identities, f, indent=4)

    logger.info("Job output written successfully.")


JOBS = {
    "avg_identities": job_avg_identities,
}


def print_help():
    logger.info("Usage:\n  python jobs.py list\n  python jobs.py <job_name>\n")
    logger.info("Available jobs:")
    for name in JOBS:
        logger.info("  - %s", name)


def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    cmd = sys.argv[1].strip().lower()

    if cmd in ("list", "--list", "-l", "help", "--help", "-h"):
        print_help()
        return

    job_fn = JOBS.get(cmd)
    if not job_fn:
        logger.error("Unknown job: %s", cmd)
        print_help()
        sys.exit(2)

    app = create_app(register_blueprints=False)

    logger.info("Running job: %s", cmd)
    try:
        job_fn(app)
    except Exception:
        logger.exception("Job failed: %s", cmd)
        sys.exit(3)

    logger.info("Done: %s", cmd)


if __name__ == "__main__":
    main()
