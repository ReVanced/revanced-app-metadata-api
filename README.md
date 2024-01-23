# ReVanced PlayStore Metadata API

## Description

The application provides search functionality for some useful metadata about PlayStore applications.

## How to Run

This project uses [Poetry](https://python-poetry.org/) for dependency management. To run the application, you need to have Poetry installed.

1. Clone the repository.
2. Navigate to the project directory.
3. Install the project dependencies with Poetry: `poetry install`
4. Set the environment variables `SEARCH_API_KEY`, `SEARCH_ENGINE_ID` and `REDIS_URL`
5. Run the application: `poetry run python app.py`
