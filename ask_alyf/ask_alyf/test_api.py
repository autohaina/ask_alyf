from unittest.mock import patch

from frappe.tests import UnitTestCase

from ask_alyf.ask_alyf import api


class UnitTestAskALYFApi(UnitTestCase):
	def make_settings(self, **overrides):
		class Settings:
			allow_agent_mode = 0
			allow_field_agent = 0
			allow_file_upload = 0
			show_file_upload_button = None
			show_voice_input_button = None
			panel_title = ""
			panel_subtitle = ""
			panel_logo = ""
			input_placeholder = ""
			panel_disclaimer = ""
			model = ""
			support_phone_number = ""

			def get_password(self, fieldname, raise_exception=False):
				return ""

		settings = Settings()
		for key, value in overrides.items():
			setattr(settings, key, value)
		return settings

	def test_can_access_ask_alyf_allows_user_with_role(self):
		with patch.object(api.frappe, "get_roles", return_value=["Desk User", api.ASK_ALYF_USER_ROLE]):
			self.assertTrue(api.can_access_ask_alyf())

	def test_can_access_ask_alyf_rejects_user_without_role(self):
		with patch.object(api.frappe, "get_roles", return_value=["Desk User"]):
			self.assertFalse(api.can_access_ask_alyf())

	def test_can_access_ask_alyf_rejects_guest(self):
		with (
			patch.dict(api.frappe.session, {"user": "Guest"}),
			patch.object(api.frappe, "get_roles", return_value=[api.ASK_ALYF_USER_ROLE]),
		):
			self.assertFalse(api.can_access_ask_alyf())

	def test_boot_payload_includes_default_panel_config(self):
		with (
			patch.object(api, "get_settings", return_value=self.make_settings()),
			patch.object(api, "can_access_ask_alyf", return_value=True),
			patch.object(api.frappe.db, "exists", return_value=True),
		):
			payload = api.get_ask_alyf_boot_payload()

		self.assertEqual(payload["panel_config"]["title"], "海纳百川")
		self.assertEqual(payload["panel_config"]["subtitle"], "AI协作助手")
		self.assertEqual(payload["panel_config"]["input_placeholder"], "请输入您的业务问题...")
		self.assertEqual(payload["panel_config"]["disclaimer"], "AI可能也会出错，包括关于数字和人员信息的内容。")
		self.assertEqual(payload["panel_config"]["logo_url"], "/assets/ask_alyf/img/aizs.gif")
		self.assertTrue(payload["panel_config"]["show_file_upload_button"])
		self.assertTrue(payload["panel_config"]["show_voice_input_button"])
		self.assertFalse(payload["file_upload_enabled"])
		self.assertTrue(payload["voice_input_enabled"])

	def test_boot_payload_uses_custom_panel_config_and_combines_upload_switches(self):
		with (
			patch.object(
				api,
				"get_settings",
				return_value=self.make_settings(
					allow_file_upload=1,
					show_file_upload_button=0,
					show_voice_input_button=0,
					panel_title="自定义标题",
					panel_subtitle="自定义副标题",
					panel_logo="/files/custom.png",
					input_placeholder="请输入测试问题",
					panel_disclaimer="自定义免责声明",
				),
			),
			patch.object(api, "can_access_ask_alyf", return_value=True),
			patch.object(api.frappe.db, "exists", return_value=True),
		):
			payload = api.get_ask_alyf_boot_payload()

		self.assertEqual(payload["panel_config"]["title"], "自定义标题")
		self.assertEqual(payload["panel_config"]["subtitle"], "自定义副标题")
		self.assertEqual(payload["panel_config"]["input_placeholder"], "请输入测试问题")
		self.assertEqual(payload["panel_config"]["disclaimer"], "自定义免责声明")
		self.assertEqual(payload["panel_config"]["logo_url"], "/files/custom.png")
		self.assertFalse(payload["panel_config"]["show_file_upload_button"])
		self.assertFalse(payload["panel_config"]["show_voice_input_button"])
		self.assertFalse(payload["file_upload_enabled"])
		self.assertFalse(payload["voice_input_enabled"])

	def test_boot_payload_uses_default_panel_switches_when_single_values_are_missing(self):
		def exists(doctype, filters=None):
			if doctype == "DocType":
				return True
			if doctype == "Singles":
				return False
			return True

		with (
			patch.object(
				api,
				"get_settings",
				return_value=self.make_settings(
					allow_file_upload=1,
					show_file_upload_button=0,
					show_voice_input_button=0,
				),
			),
			patch.object(api, "can_access_ask_alyf", return_value=True),
			patch.object(api.frappe.db, "exists", side_effect=exists),
		):
			payload = api.get_ask_alyf_boot_payload()

		self.assertTrue(payload["panel_config"]["show_file_upload_button"])
		self.assertTrue(payload["panel_config"]["show_voice_input_button"])
		self.assertTrue(payload["file_upload_enabled"])
		self.assertTrue(payload["voice_input_enabled"])
