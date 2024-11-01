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
├── readme_content/            # Supplementary files for README
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
---
# Media

### Demonstrating advanced filtering and querying capabilities, powered by SQLAlchemy ORM to interface with a PostgreSQL database. Features include data comparison through Chart.js visualizations like histograms, 8D-PolComp charts, and individual question analysis, with custom CSS animations and formatting.
![ChartJS](readme_content/data.gif)

### Showcasing the mobile-friendly, responsive layout of the web app, built with Flexbox, CSS Grid, and media queries for seamless adaptability across devices. Dynamic element sizing with percentage widths, alongside rem and em units.
![Responsive Layout](readme_content/responsive.gif)

### Demonstrating interactive results charts and graphs powered by Chart.js, featuring customisable options, intuitive formatting, and responsive design for dynamic data exploration.
![ChartJS](readme_content/chart_js.gif)


### A questionnaire with data served from PostgreSQL. Includes a form with Google reCAPTCHA for security, analytics tracking, and final results submitted to a PostgreSQL results table.
![ChartJS](readme_content/test.gif)
