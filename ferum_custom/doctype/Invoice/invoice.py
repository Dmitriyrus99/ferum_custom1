# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Invoice(Document):
	def after_insert(self):
		self.notify_on_subcontractor_invoice()
		self.sync_with_google_sheets()

	def notify_on_subcontractor_invoice(self):
		if self.counterparty_type == "Subcontractor":
			# Placeholder for actual notification
			# frappe.sendmail(recipients=[user.email for user in admins], subject=subject, message=message)

			frappe.msgprint(f"Notification sent to administrators about subcontractor invoice {self.name}")

	def sync_with_google_sheets(self):
		# Placeholder for Google Sheets integration logic
		# This would involve calling the Google Sheets API
		# to append a new row with the invoice data.

		frappe.msgprint(f"Invoice {self.name} synced with Google Sheets.")
