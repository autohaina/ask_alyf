// Copyright (c) 2026, ALYF GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Ask ALYF Skill", {
	refresh(frm) {
		render_skill_roles_editor(frm);
	},

	validate(frm) {
		frm.roles_editor?.set_roles_in_table();
	},
});

function render_skill_roles_editor(frm) {
	if (!frm.fields_dict.roles_html) {
		return;
	}

	if (!frm.roles_editor) {
		const role_area = $('<div class="role-editor">').appendTo(frm.fields_dict.roles_html.wrapper);
		frm.roles_editor = new frappe.RoleEditor(role_area, frm);
	}

	frm.roles_editor.show();
}
