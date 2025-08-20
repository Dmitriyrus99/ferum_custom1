import json

import frappe
import requests
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, add_hours, getdate, nowdate


class ServiceRequest(Document):
    def validate(self):
        self.set_customer_and_project()
        self.validate_workflow_transitions()
        self.calculate_sla_deadline()

    def on_update(self):
        self.check_sla_breach()

    def set_customer_and_project(self):
        if self.is_new() or self.has_value_changed("service_object"):
            if self.service_object:
                service_object_doc = frappe.get_doc("ServiceObject", self.service_object)
                self.customer = service_object_doc.customer
                self.project = service_object_doc.project
            else:
                self.customer = None
                self.project = None

    def validate_workflow_transitions(self):
        # Implement strict workflow transitions based on Technical_Specification_full.md
        # [*] --> Open
        # Open --> InProgress : Assign Engineer
        # InProgress --> Completed : Submit Service Report
        # Completed --> Closed : Manager Approval

        # Get old status if document is not new
        old_status = frappe.db.get_value("ServiceRequest", self.name, "status") if not self.is_new() else None

        if old_status == "Open" and self.status == "In Progress" and not self.assigned_to:
            frappe.throw(_("Cannot set status to 'In Progress' without assigning an engineer."))
        elif old_status == "In Progress" and self.status == "Completed" and not self.linked_report:
            frappe.throw(_("Cannot set status to 'Completed' without linking a Service Report."))
        elif old_status == "Completed" and self.status == "Closed" and "System Manager" not in frappe.get_roles(): # Placeholder for Manager Approval
            # In a real scenario, this would check for a specific role or user
            frappe.throw(_("Only a Manager can close a Service Request."))
        # Add more transitions as needed based on the full workflow diagram
        # For example, Open -> Cancelled, In Progress -> Cancelled, Completed -> In Progress (for rework)
        # For simplicity, I'm only adding the main positive flow and a basic check for closing.

    def calculate_sla_deadline(self):
        # Placeholder for SLA calculation logic
        # This would typically involve business hours, holidays, etc.
        # For now, a simple calculation based on type and priority
        if self.type == "Emergency" and self.priority == "High":
            self.sla_deadline = add_hours(self.creation, 4) # 4 hours for high emergency
        elif self.type == "Emergency" and self.priority == "Medium":
            self.sla_deadline = add_hours(self.creation, 8) # 8 hours for medium emergency
        elif self.type == "Routine" and self.priority == "High":
            self.sla_deadline = add_days(self.creation, 1) # 1 day for routine high
        else:
            self.sla_deadline = add_days(self.creation, 3) # 3 days for others

    def check_sla_breach(self):
        if self.status not in ["Completed", "Closed"] and self.sla_deadline and getdate(nowdate()) > getdate(self.sla_deadline):
            message = f"SLA for Service Request {self.name} has been breached! Title: {self.title}. Priority: {self.priority}. Due: {self.sla_deadline}"
            frappe.msgprint(_(message))
            frappe.log_error(message, "SLA Breach Alert")

            # Enqueue the notification sending to a background job
            frappe.enqueue(
                "ferum_custom.doctype.service_request.service_request.send_sla_breach_notifications",
                service_request_name=self.name,
                message=message
            )

@frappe.whitelist()
def send_sla_breach_notifications(service_request_name, message):
    if not frappe.has_permission("ServiceRequest", "read", doc=service_request_name):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    settings = frappe.get_single("Ferum Settings")

    # Send Telegram notification
    if settings.enable_telegram_notifications and settings.telegram_chat_id and settings.fastapi_url:
        try:
            token = settings.get_password("fastapi_jwt_token")
            headers = {"Authorization": f"Bearer {token}"}
            payload = {"chat_id": settings.telegram_chat_id, "text": message}
            response = requests.post(f"{settings.fastapi_url}/api/v1/send_telegram_notification", headers=headers, json=payload)
            response.raise_for_status()
            frappe.log_by_page(f"SLA breach notification sent to Telegram for {service_request_name}", "SLA Notification")
        except Exception as e:
            frappe.log_error(f"Failed to send SLA breach Telegram notification for {service_request_name}: {e}", "SLA Notification Error")

    # Send Email notification
    if settings.enable_email_notifications and settings.sla_breach_recipient_email:
        try:
            subject = f"SLA Breach Alert: Service Request {service_request_name}"
            frappe.sendmail(recipients=settings.sla_breach_recipient_email, subject=subject, message=message)
            frappe.log_by_page(f"SLA breach email notification sent for {service_request_name}", "SLA Notification")
        except Exception as e:
            frappe.log_error(f"Failed to send SLA breach email notification for {service_request_name}: {e}", "SLA Notification Error")
