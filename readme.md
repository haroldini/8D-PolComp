# 8D-PolComp

8D-PolComp is a comprehensive political test and data analysis web application designed to assess users' ideological alignment across eight distinct political axes, such as economics, governance, and social values. The platform allows users to submit and compare their results with others, view data visualizations, and explore trends among different demographics.

## Project Structure
```bash
8D-PolComp/
│   8dpolcomp/
│   ├── application/
│   │   ├── controllers/       # Controllers for data logic
│   │   ├── data/              # JSON and CSV data files for demographics and exports
│   │   ├── models/            # SQLAlchemy models for database interaction
│   │   ├── static/            # Static assets (CSS, JS, images)
│   │   ├── templates/         # HTML templates
│   │   │   ├── components/    # Reusable HTML components (e.g., ChartJS elements)
│   │   │   ├── layouts/       # Site-wide templates (e.g., footer.html, header.html)
│   │   │   └── pages/         # Page-specific templates (e.g., contact.html, index.html)
│   │   └── views/             # Flask view blueprints for different sections
│   ├── config/                # Configuration files
│   ├── cronjobs/              # Scheduled tasks or background jobs
│   └── run.py                 # Main entry point to run the application
├── env/                       # Virtual environment directory
├── resources/                 # Additional resources or documentation
├── readme-content/            # Supplementary files for README
├── .gitignore                 # Git ignore file
├── README.md                  # Project README
└── requirements.txt           # Project dependencies
```
  
## Dependencies

The project uses the following key libraries:

- **Flask** (v3.0.3): The web framework used to handle requests, routes, and render templates.
- **SQLAlchemy** and **Flask-SQLAlchemy** (v3.1.1): ORM for interacting with the database, managing models, and performing queries.
- **NumPy** (v2.1.2): For handling numeric operations, such as calculating mean and median scores.
- **Requests** (v2.32.3): For making HTTP requests if needed.
- **scikit-learn** (v1.5.2): Provides the `MaxAbsScaler` for scaling data in data visualizations.
- **sqlalchemy-filtering** (v0.1.2): Used for advanced querying and filtering of data based on user-defined criteria.

