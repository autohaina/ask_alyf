import frappe
from frappe.model.document import Document
from frappe.query_builder import Interval
from frappe.query_builder.functions import Now


class AskALYFConversation(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		last_context_json: DF.Code | None
		last_message_at: DF.Datetime | None
		messages_json: DF.Code | None
		pending_operation_json: DF.Code | None
		route: DF.Data | None
		status: DF.Literal["Active", "Closed"]
		title: DF.Data
	# end: auto-generated types

	@staticmethod
	def clear_old_logs(days: int = 90):
		table = frappe.qb.DocType("Ask ALYF Conversation")
		frappe.db.delete(table, filters=(table.creation < (Now() - Interval(days=days))))
