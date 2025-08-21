from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.auth import get_current_user
from backend.main import app

client = TestClient(app)


def test_update_request_status_as_assigned_engineer():
	app.dependency_overrides[get_current_user] = lambda: {"name": "test_engineer", "roles": ["Engineer"]}
	with patch("backend.routers.requests.frappe_client") as mock_frappe_client:
		mock_frappe_client.get_doc.return_value = {"name": "SR-001", "assigned_to": "test_engineer"}
		response = client.put("/api/v1/requests/SR-001/status", json={"status": "In Progress"})
		assert response.status_code == 200
	app.dependency_overrides = {}


def test_update_request_status_as_unassigned_engineer():
	app.dependency_overrides[get_current_user] = lambda: {"name": "other_engineer", "roles": ["Engineer"]}
	with patch("backend.routers.requests.frappe_client") as mock_frappe_client:
		mock_frappe_client.get_doc.return_value = {"name": "SR-001", "assigned_to": "test_engineer"}
		response = client.put("/api/v1/requests/SR-001/status", json={"status": "In Progress"})
		assert response.status_code == 403
	app.dependency_overrides = {}


def test_update_request_status_as_admin():
	app.dependency_overrides[get_current_user] = lambda: {"name": "admin", "roles": ["Administrator"]}
	with patch("backend.routers.requests.frappe_client") as mock_frappe_client:
		mock_frappe_client.get_doc.return_value = {"name": "SR-001", "assigned_to": "test_engineer"}
		response = client.put("/api/v1/requests/SR-001/status", json={"status": "In Progress"})
		assert response.status_code == 200
	app.dependency_overrides = {}
