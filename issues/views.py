from datetime import datetime

from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from .models import CriticalIssue, Issue, LowPriorityIssue, Reporter
from .storage import next_id, read_records, write_records

REPORTERS_FILE = "reporters.json"
ISSUES_FILE = "issues.json"


def _error(message, status=400):
    return Response({"error": message}, status=status)


def _body_data(request):
    try:
        data = request.data
    except ParseError:
        raise ValueError("Request body must contain valid JSON")
    if not isinstance(data, dict):
        raise ValueError("Request body must be a JSON object")
    return data


def _requested_id(request):
    value = request.query_params.get("id")
    if value is None:
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValueError("id must be a positive integer")
    if parsed < 1:
        raise ValueError("id must be a positive integer")
    return parsed


def _list_or_get_one(request, filename, singular):
    try:
        records = read_records(filename)
        record_id = _requested_id(request)
    except ValueError as exc:
        return _error(str(exc))
    except RuntimeError:
        return _error("Stored data is unavailable or invalid", 500)
    if record_id is not None:
        record = next((item for item in records if item.get("id") == record_id), None)
        if record is None:
            return _error(f"{singular} not found", 404)
        return Response(record, status=200)
    return Response(records, status=200)


@api_view(["GET", "POST"])
def reporters(request):
    if request.method == "GET":
        return _list_or_get_one(request, REPORTERS_FILE, "Reporter")
    if request.method != "POST":
        response = _error("Method not allowed", 405)
        response["Allow"] = "GET, POST"
        return response
    try:
        data = _body_data(request)
        records = read_records(REPORTERS_FILE)
        new_id = data.get("id", next_id(records))
        if isinstance(new_id, bool) or not isinstance(new_id, int) or new_id < 1:
            raise ValueError("id must be a positive integer")
        if any(item.get("id") == new_id for item in records):
            raise ValueError("Reporter ID already exists")
        reporter = Reporter(new_id, data.get("name"), data.get("email"), data.get("team"))
        reporter.validate()
        record = reporter.to_dict()
        records.append(record)
        write_records(REPORTERS_FILE, records)
        return Response(record, status=201)
    except ValueError as exc:
        return _error(str(exc))
    except RuntimeError:
        return _error("Stored data is unavailable or invalid", 500)

@api_view(["GET", "POST"])
def issues(request):
    if request.method == "GET":
        try:
            records = read_records(ISSUES_FILE)
            issue_id = _requested_id(request)
        except ValueError as exc:
            return _error(str(exc))
        except RuntimeError:
            return _error("Stored data is unavailable or invalid", 500)
        if issue_id is not None:
            record = next((item for item in records if item.get("id") == issue_id), None)
            return Response(record, status=200) if record else _error("Issue not found", 404)
        issue_status = request.query_params.get("status")
        if issue_status is not None:
            if issue_status not in Issue.STATUSES:
                return _error("Status must be one of: " + ", ".join(sorted(Issue.STATUSES)))
            records = [record for record in records if record.get("status") == issue_status]
        return Response(records, status=200)

    if request.method != "POST":
        response = _error("Method not allowed", 405)
        response["Allow"] = "GET, POST"
        return response
    try:
        data = _body_data(request)
        records = read_records(ISSUES_FILE)
        reporter_id = data.get("reporter_id")
        if isinstance(reporter_id, bool) or not isinstance(reporter_id, int) or reporter_id < 1:
            raise ValueError("reporter_id must be a positive integer")
        reporter_records = read_records(REPORTERS_FILE)
        if not any(record.get("id") == reporter_id for record in reporter_records):
            return _error("Reporter not found", 404)
        issue_id = data.get("id", next_id(records))
        if isinstance(issue_id, bool) or not isinstance(issue_id, int) or issue_id < 1:
            raise ValueError("id must be a positive integer")
        if any(item.get("id") == issue_id for item in records):
            raise ValueError("Issue ID already exists")
        values = (issue_id, data.get("title"), data.get("description", ""),
            data.get("status"), data.get("priority"), reporter_id)
        if data.get("priority") == "critical":
            issue = CriticalIssue(*values)
        elif data.get("priority") == "low":
            issue = LowPriorityIssue(*values)
        else:
            issue = Issue(*values)
        issue.validate()
        record = issue.to_dict()
        record["created_at"] = data.get("created_at") or datetime.now().astimezone().isoformat()
        record["message"] = issue.describe()
        records.append(record)
        write_records(ISSUES_FILE, records)
        return Response(record, status=201)
    except ValueError as exc:
        return _error(str(exc))
    except RuntimeError:
        return _error("Stored data is unavailable or invalid", 500)
