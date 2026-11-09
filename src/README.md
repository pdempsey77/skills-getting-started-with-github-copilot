# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.

## Testing

Run these commands from the repository root to install the application and test
dependencies, then run the backend suite:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

Backend tests live in [`tests/`](../tests/). Each test uses explicit
Arrange-Act-Assert (AAA) sections: prepare inputs and expected results, make the
request, then check the response and state changes. The suite uses FastAPI's
TestClient without starting a server.

Shared fixtures in [`tests/conftest.py`](../tests/conftest.py) give every test a
deep copy of the in-memory activity data and restore the original mapping
afterward, so participant changes cannot leak between tests.

The suite covers activity listing, signup, unregistering, success and error
responses, required email query parameters, and the root redirect/static HTML
page. It tests existing backend behavior, not frontend JavaScript or new
capacity/email-validation rules.

The [backend test workflow](../.github/workflows/backend-tests.yml) runs the same
installation and test commands on pushes and pull requests using Python 3.13,
matching the dev container. It is separate from the exercise workflows.
