# Dev Bug Track

A small Django backend for tracking engineering issues. The Django app is `issues`. Its domain entities are plain Python classes in `issues/models.py`; the API persists records in `reporters.json` and `issues.json` as required by the project brief.

## Run locally

From the repository root, activate the virtual environment and start Django:

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000/api/`. JSON files are created/read in the repository root. Back them up before clearing or editing stored data.

## Endpoints

All request and response bodies use JSON. POST requests accept `Content-Type: application/json`.

| Method and path                | Purpose                                                                                                                                         |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `POST /api/reporters/`         | Create a reporter. Required fields: `name`, `email`, `team`; `id` is optional and assigned automatically when omitted.                          |
| `GET /api/reporters/`          | List reporters.                                                                                                                                 |
| `GET /api/reporters/?id=1`     | Get a reporter by ID (404 when absent).                                                                                                         |
| `POST /api/issues/`            | Create an issue. Required fields: `title`, `status`, `priority`, `reporter_id`; `description` defaults to an empty string and `id` is optional. |
| `GET /api/issues/`             | List issues.                                                                                                                                    |
| `GET /api/issues/?id=1`        | Get an issue by ID (404 when absent).                                                                                                           |
| `GET /api/issues/?status=open` | Filter issues by status.                                                                                                                        |

Allowed statuses: `open`, `in_progress`, `resolved`, `closed`. Allowed priorities: `low`, `medium`, `high`, `critical`. Creating an issue requires an existing reporter. Critical and low priority issues include a priority-specific `message` in the response. Invalid input returns a JSON `error` with HTTP 400; missing records return 404.

## Example requests

Create a reporter:

```json
{
  "name": "Alex Morgan",
  "email": "alex@example.com",
  "team": "backend"
}
```

Create an issue using the returned reporter ID:

```json
{
  "title": "Login button not working on mobile",
  "description": "Users on iOS 17 cannot tap the login button",
  "status": "open",
  "priority": "critical",
  "reporter_id": 1
}
```

## Design decision

The issue stores `reporter_id`, so one reporter can be referenced by many issues without duplicating reporter details. The JSON repository uses atomic file replacement to avoid leaving a partially written JSON document if a process is interrupted during a save. This storage choice is appropriate for the exercise; a database is a better fit for multi-process or production workloads.

## Postman evidence

Import the API URLs above into Postman and save screenshots of a successful request and a validation failure here before submission. Example failure: POST an issue with an empty `title` and capture the HTTP 400 JSON response.

Tested VS code echo API's screenshots were added in below notion page.
https://app.notion.com/p/Dev-Track-3e55d101bf168096b9b8d2c9fa3b0145?source=copy_link
