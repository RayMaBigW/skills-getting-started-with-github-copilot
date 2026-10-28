# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- Unregister participants from activities using the delete icon next to their email

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
| DELETE | `/activities/{activity_name}/signup?email=student@mergington.edu` | Unregister a participant from an activity                           |

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

## Backend Tests

From the repository root, install the dependencies and run the backend suite:

```sh
python -m pip install -r requirements.txt
python -m pytest tests -v
```

The tests use pytest and FastAPI's `TestClient`; no running server or Uvicorn
process is required. Shared fixtures in [tests/conftest.py](../tests/conftest.py)
provide a context-managed client and restore the in-memory activity dictionary
after every test, including failed tests.

Every backend test uses explicit **Arrange–Act–Assert (AAA)** sections:

- **Arrange:** Prepare scenario-specific participants, parameters, and expected state.
- **Act:** Make the request being tested and capture its response. A follow-up
   listing request can observe the updated state.
- **Assert:** Check response status, JSON data, and state changes (or lack of changes).
   Mutation requests do not belong inside assertions.

Coverage includes the root redirect, activity listing, successful and duplicate
signup, unknown activities, required email validation, participant removal,
repeated removal, re-registration, and removal of the final participant.
Capacity and email-format validation are not enforced by the current API and
are outside this suite's scope.

The JavaScript regression tests remain separate and can be run with:

```sh
node --test tests/signup-refresh.test.cjs
```
