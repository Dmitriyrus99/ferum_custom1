from unittest.mock import MagicMock, patch

from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from backend.auth import get_current_user
from backend.main import app

client = TestClient(app)

# --- Mock Data ---
mock_accountant_user = {"name": "test_accountant", "roles": ["Accountant"]}
mock_project_manager_user = {
	"name": "test_pm",
	"roles": ["Project Manager"],
	"managed_projects": ["PROJ-001", "PROJ-002"],
}
mock_client_user = {"name": "test_client", "roles": ["Client"], "customer_id": "CUST-001"}
mock_unauthorized_user = {"name": "unauthorized", "roles": ["Guest"]}

mock_all_invoices = [
	{
		"name": "INV-001",
		"project": "PROJ-001",
		"amount": 100,
		"status": "Draft",
		"counterparty_type": "Customer",
		"customer": "CUST-001",
	},
	{
		"name": "INV-002",
		"project": "PROJ-002",
		"amount": 200,
		"status": "Sent",
		"counterparty_type": "Customer",
		"customer": "CUST-002",
	},
	{
		"name": "INV-003",
		"project": "PROJ-003",
		"amount": 300,
		"status": "Paid",
		"counterparty_type": "Subcontractor",
		"customer": "CUST-003",
	},
]

mock_pm_invoices = [
	{
		"name": "INV-001",
		"project": "PROJ-001",
		"amount": 100,
		"status": "Draft",
		"counterparty_type": "Customer",
		"customer": "CUST-001",
	},
	{
		"name": "INV-002",
		"project": "PROJ-002",
		"amount": 200,
		"status": "Sent",
		"counterparty_type": "Customer",
		"customer": "CUST-002",
	},
]

mock_client_invoices = [
	{
		"name": "INV-001",
		"project": "PROJ-001",
		"amount": 100,
		"status": "Draft",
		"counterparty_type": "Customer",
		"customer": "CUST-001",
	},
]

mock_single_invoice = {
	"name": "INV-001",
	"project": "PROJ-001",
	"amount": 100,
	"status": "Draft",
	"counterparty_type": "Customer",
	"customer": "CUST-001",
}


# --- Health Check ---
def test_health_check():
	response = client.get("/api/v1/health")
	assert response.status_code == 200
	assert response.json() == {"status": "ok"}


# --- Invoices Router Tests ---


# Helper to override get_current_user dependency
def override_get_current_user(user_data: dict):
	async def _override():
		return user_data

	return _override


# Helper to mock frappe_client
def mock_frappe_client(
	get_list_return=None,
	get_doc_return=None,
	get_value_return=None,
	insert_return=None,
	set_value_return=None,
):
	mock = MagicMock()
	if get_list_return is not None:
		mock.get_list.return_value = get_list_return
	if get_doc_return is not None:
		if isinstance(get_doc_return, Exception):
			mock.get_doc.side_effect = get_doc_return
		elif isinstance(get_doc_return, MagicMock) and get_doc_return.side_effect:
			mock.get_doc.side_effect = get_doc_return.side_effect
		else:
			mock.get_doc.return_value = get_doc_return
	if get_value_return is not None:
		mock.get_value.return_value = get_value_return
	if insert_return is not None:
		mock.insert.return_value = insert_return
	if set_value_return is not None:
		mock.set_value.return_value = set_value_return
	return mock


# Test GET /invoices
def test_get_invoices_as_accountant():
	with patch(
		"backend.routers.invoices.frappe_client", mock_frappe_client(get_list_return=mock_all_invoices)
	):
		app.dependency_overrides[get_current_user] = override_get_current_user(mock_accountant_user)
		response = client.get("/api/v1/invoices")
		assert response.status_code == 200
		assert response.json() == {"invoices": mock_all_invoices}
	app.dependency_overrides = {}  # Clean up


def test_get_invoices_as_project_manager():
	with patch(
		"backend.routers.invoices.frappe_client", mock_frappe_client(get_list_return=mock_pm_invoices)
	):
		app.dependency_overrides[get_current_user] = override_get_current_user(mock_project_manager_user)
		response = client.get("/api/v1/invoices")
		assert response.status_code == 200
		assert response.json() == {"invoices": mock_pm_invoices}
	app.dependency_overrides = {}


def test_get_invoices_as_client():
	with patch(
		"backend.routers.invoices.frappe_client", mock_frappe_client(get_list_return=mock_client_invoices)
	):
		app.dependency_overrides[get_current_user] = override_get_current_user(mock_client_user)
		response = client.get("/api/v1/invoices")
		assert response.status_code == 200
		assert response.json() == {"invoices": mock_client_invoices}
	app.dependency_overrides = {}


def test_get_invoices_unauthorized():
	# Simulate no user (e.g., no token)
	app.dependency_overrides[get_current_user] = lambda: (_ for _ in ()).throw(
		HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
	)
	response = client.get("/api/v1/invoices")
	assert response.status_code == status.HTTP_401_UNAUTHORIZED
	app.dependency_overrides = {}


def test_get_invoices_forbidden_role():
	# Simulate a role that has no access to invoices
	app.dependency_overrides[get_current_user] = override_get_current_user(mock_unauthorized_user)
	response = client.get("/api/v1/invoices")
	assert response.status_code == status.HTTP_403_FORBIDDEN
	app.dependency_overrides = {}


# Test GET /invoices/{invoice_name}
def test_get_single_invoice_as_accountant():
	with patch(
		"backend.routers.invoices.frappe_client", mock_frappe_client(get_doc_return=mock_single_invoice)
	):
		app.dependency_overrides[get_current_user] = override_get_current_user(mock_accountant_user)
		response = client.get("/api/v1/invoices/INV-001")
		assert response.status_code == 200
		assert response.json() == {"invoice": mock_single_invoice}
	app.dependency_overrides = {}


def test_get_single_invoice_as_project_manager_authorized():
	with patch(
		"backend.routers.invoices.frappe_client", mock_frappe_client(get_doc_return=mock_single_invoice)
	):
		app.dependency_overrides[get_current_user] = override_get_current_user(mock_project_manager_user)
		response = client.get("/api/v1/invoices/INV-001")
		assert response.status_code == 200
		assert response.json() == {"invoice": mock_single_invoice}
	app.dependency_overrides = {}


def test_get_single_invoice_as_project_manager_forbidden():
	# Mock an invoice not managed by the PM
	mock_other_invoice = {
		"name": "INV-999",
		"project": "PROJ-999",
		"amount": 500,
		"status": "Draft",
		"counterparty_type": "Customer",
		"customer": "CUST-999",
	}
	with patch(
		"backend.routers.invoices.frappe_client", mock_frappe_client(get_doc_return=mock_other_invoice)
	):
		app.dependency_overrides[get_current_user] = override_get_current_user(mock_project_manager_user)
		response = client.get("/api/v1/invoices/INV-999")
		assert response.status_code == status.HTTP_403_FORBIDDEN
	app.dependency_overrides = {}


def test_get_single_invoice_as_client_authorized():
	with patch(
		"backend.routers.invoices.frappe_client", mock_frappe_client(get_doc_return=mock_single_invoice)
	):
		app.dependency_overrides[get_current_user] = override_get_current_user(mock_client_user)
		response = client.get("/api/v1/invoices/INV-001")
		assert response.status_code == 200
		assert response.json() == {"invoice": mock_single_invoice}
	app.dependency_overrides = {}


def test_get_single_invoice_as_client_forbidden():
	# Mock an invoice not belonging to the client
	mock_other_invoice = {
		"name": "INV-999",
		"project": "PROJ-999",
		"amount": 500,
		"status": "Draft",
		"counterparty_type": "Customer",
		"customer": "CUST-999",
	}
	with patch(
		"backend.routers.invoices.frappe_client", mock_frappe_client(get_doc_return=mock_other_invoice)
	):
		app.dependency_overrides[get_current_user] = override_get_current_user(mock_client_user)
		response = client.get("/api/v1/invoices/INV-999")
		assert response.status_code == status.HTTP_403_FORBIDDEN
	app.dependency_overrides = {}


def test_get_single_invoice_not_found():
	with patch(
		"backend.routers.invoices.frappe_client",
		mock_frappe_client(
			get_doc_return=MagicMock(side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND))
		),
	):
		app.dependency_overrides[get_current_user] = override_get_current_user(mock_accountant_user)
		response = client.get("/api/v1/invoices/NON-EXISTENT")
		assert response.status_code == status.HTTP_404_NOT_FOUND
	app.dependency_overrides = {}


def test_get_single_invoice_unauthorized():
	app.dependency_overrides[get_current_user] = lambda: (_ for _ in ()).throw(
		HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
	)
	response = client.get("/api/v1/invoices/INV-001")
	assert response.status_code == status.HTTP_401_UNAUTHORIZED
	app.dependency_overrides = {}


# Test POST /invoices
def test_create_invoice_as_project_manager():
	new_invoice_data = {"project": "PROJ-001", "amount": 150, "status": "Draft"}
	mock_created_invoice = {"name": "INV-NEW", **new_invoice_data}
	with patch(
		"backend.routers.invoices.frappe_client", mock_frappe_client(insert_return=mock_created_invoice)
	):
		app.dependency_overrides[get_current_user] = override_get_current_user(mock_project_manager_user)
		with patch(
			"backend.routers.invoices.has_role", return_value=MagicMock()
		):  # Mock has_role to allow access
			response = client.post("/api/v1/invoices", json=new_invoice_data)
			assert response.status_code == 200
			assert response.json()["message"] == "Invoice created successfully"
			assert response.json()["invoice"]["name"] == "INV-NEW"
	app.dependency_overrides = {}


def test_create_invoice_forbidden_role():
	new_invoice_data = {"project": "PROJ-001", "amount": 150, "status": "Draft"}
	app.dependency_overrides[get_current_user] = override_get_current_user(
		mock_client_user
	)  # Client cannot create
	with patch(
		"backend.routers.invoices.has_role", side_effect=HTTPException(status_code=status.HTTP_403_FORBIDDEN)
	):  # Simulate has_role denying access
		response = client.post("/api/v1/invoices", json=new_invoice_data)
		assert response.status_code == status.HTTP_403_FORBIDDEN
	app.dependency_overrides = {}


# Test PUT /invoices/{invoice_name}/status
def test_update_invoice_status_as_accountant():
	status_data = {"status": "Paid"}
	mock_updated_invoice = {"name": "INV-001", "status": "Paid"}
	with patch(
		"backend.routers.invoices.frappe_client", mock_frappe_client(set_value_return=mock_updated_invoice)
	):
		app.dependency_overrides[get_current_user] = override_get_current_user(mock_accountant_user)
		with patch(
			"backend.routers.invoices.has_role", return_value=MagicMock()
		):  # Mock has_role to allow access
			response = client.put("/api/v1/invoices/INV-001/status", json=status_data)
			assert response.status_code == 200
			assert response.json()["message"] == "Invoice status updated successfully"
			assert response.json()["invoice"]["status"] == "Paid"
	app.dependency_overrides = {}


def test_update_invoice_status_forbidden_role():
	status_data = {"status": "Paid"}
	app.dependency_overrides[get_current_user] = override_get_current_user(
		mock_client_user
	)  # Client cannot update status
	with patch(
		"backend.routers.invoices.has_role", side_effect=HTTPException(status_code=status.HTTP_403_FORBIDDEN)
	):  # Simulate has_role denying access
		response = client.put("/api/v1/invoices/INV-001/status", json=status_data)
		assert response.status_code == status.HTTP_403_FORBIDDEN
	app.dependency_overrides = {}
