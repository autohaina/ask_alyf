# Copyright (c) 2026, ALYF GmbH and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AskALYFSkill(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.core.doctype.has_role.has_role import HasRole
		from frappe.types import DF

		description: DF.MarkdownEditor
		roles: DF.Table[HasRole]
		title: DF.Data
	# end: auto-generated types

	pass
