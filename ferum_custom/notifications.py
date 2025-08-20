import json

import frappe
import requests


def send_telegram_notification_via_fastapi(chat_id, message):
    """Fetches config from Ferum Settings and sends a Telegram notification via the FastAPI backend."""
    settings = frappe.get_single("Ferum Settings")

    if not settings.enable_telegram_notifications or not settings.fastapi_url or not chat_id:
        return

    try:
        token = settings.get_password("fastapi_jwt_token")
        if not token:
            frappe.log_error("FastAPI JWT Token not set in Ferum Settings", "Notification Error")
            return

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "chat_id": chat_id,
            "text": message
        }
        
        # Note: The actual requests call is now wrapped in a background job by the calling functions.
        # This function is the background job itself.
        response = requests.post(f"{settings.fastapi_url}/api/v1/send_telegram_notification", headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        frappe.log_by_page(f"Telegram notification sent via FastAPI for chat_id {chat_id}", "Notification Success")

    except Exception as e:
        frappe.log_error(f"Failed to send Telegram notification via FastAPI to chat_id {chat_id}: {e}", "Notification Error")


def get_chat_id_for_user(user):
    """Placeholder function to get Telegram Chat ID for a given user."""
    # In a real implementation, you would have a custom field 'telegram_chat_id' in the User DocType.
    # return frappe.db.get_value("User", user, "custom_telegram_chat_id")
    # For now, returning a placeholder from settings.
    return frappe.get_single("Ferum Settings").fallback_telegram_chat_id


def get_chat_id_for_customer(customer):
    """Placeholder function to get Telegram Chat ID for a given customer."""
    # You would have a custom field 'telegram_chat_id' in the Customer or Contact DocType.
    # return frappe.db.get_value("Customer", customer, "custom_telegram_chat_id")
    return frappe.get_single("Ferum Settings").fallback_telegram_chat_id


def get_chat_ids_for_roles(roles):
    """Placeholder function to get all chat IDs for users with given roles."""
    # This is a simplified example. A real implementation would be more complex.
    # and might involve a custom mapping DocType.
    return [frappe.get_single("Ferum Settings").fallback_telegram_chat_id]


def enqueue_notification(chat_ids, message):
    """Helper function to enqueue notifications for a list of chat_ids."""
    for chat_id in chat_ids:
        if chat_id:
            frappe.enqueue(
                "ferum_custom.notifications.send_telegram_notification_via_fastapi",
                chat_id=chat_id,
                message=message
            )

# --- DocType Notification Hooks ---

def notify_new_service_request(doc, method):
    message = f"New Service Request created: {doc.name} - {doc.title}. Status: {doc.status}. Priority: {doc.priority}."
    chat_ids = get_chat_ids_for_roles(["Project Manager", "Office Manager"])
    enqueue_notification(chat_ids, message)

def notify_service_request_status_change(doc, method):
    message = f"Service Request {doc.name} status changed to {doc.status}. Title: {doc.title}."
    chat_ids = set()
    if doc.assigned_to:
        chat_ids.add(get_chat_id_for_user(doc.assigned_to))
    if doc.customer:
        chat_ids.add(get_chat_id_for_customer(doc.customer))
    enqueue_notification(list(chat_ids), message)

def notify_new_service_report(doc, method):
    message = f"New Service Report created: {doc.name} for Service Request {doc.service_request}. Status: {doc.status}."
    chat_ids = get_chat_ids_for_roles(["Project Manager", "System Manager"])
    enqueue_notification(chat_ids, message)

def notify_service_report_status_change(doc, method):
    message = f"Service Report {doc.name} status changed to {doc.status}. For Service Request {doc.service_request}."
    chat_ids = get_chat_ids_for_roles(["Project Manager", "System Manager"])
    enqueue_notification(chat_ids, message)


def notify_new_invoice(doc, method):
    message = f"New Invoice created: {doc.name} for {doc.counterparty_name}. Amount: {doc.amount}. Status: {doc.status}."
    chat_ids = get_chat_ids_for_roles(["Accountant", "System Manager"])
    enqueue_notification(chat_ids, message)

def notify_invoice_status_change(doc, method):
    message = f"Invoice {doc.name} status changed to {doc.status}. For {doc.counterparty_name}. Amount: {doc.amount}."
    chat_ids = get_chat_ids_for_roles(["Accountant", "System Manager"])
    enqueue_notification(chat_ids, message)
