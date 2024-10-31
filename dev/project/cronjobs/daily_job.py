import json
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from application import create_app
from application.controllers.results import ResultsController as Results

class DailyJob():
    """Runs once per day in scheduled task"""
    def __init__(self, app):
        self.app = app
        self.run()

    def run(self):
        with self.app.app_context():
            self.save_avg_identities()

    def save_avg_identities(self):
        """Calculates average values for each axis for each identity, saves to axis_averages"""
        """Used to determine closest matching identities"""
        demo_path = os.path.join(project_root, "application/data/demographics/demographics.json")
        avgs_path = os.path.join(project_root, "application/data/demographics/axis_averages.json")
        
        with open(demo_path, 'r', encoding='utf-8') as f:
            demographics = json.load(f)
            identities = demographics["identities"]
            identities.append("Average Result")
        
        with open(avgs_path, 'w', encoding='utf-8') as f:
            avg_identities = Results.get_avg_identities(identities, min_results=50)
            json.dump(avg_identities, f, indent=4)


if __name__ == "__main__":
    app_instance = create_app()
    dj = DailyJob(app_instance)