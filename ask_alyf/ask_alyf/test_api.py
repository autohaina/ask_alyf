from unittest.mock import Mock, patch
from types import SimpleNamespace

from frappe.tests import UnitTestCase

from ask_alyf.ask_alyf import api


class UnitTestAskALYFApi(UnitTestCase):
	def make_conversation_doc(self, **overrides):
		doc = SimpleNamespace(
			name="CONV-1",
			title="New Conversation",
			status="Active",
			route="",
			messages_json="[]",
			pending_operation_json="",
			last_context_json="",
			insert=Mock(),
			save=Mock(),
			check_permission=Mock(),
		)
		for key, value in overrides.items():
			setattr(doc, key, value)
		return doc

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
			suggested_prompts = []
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
		self.assertEqual(payload["suggested_prompts"], [])
		self.assertFalse(payload["suggested_prompts_configured"])

	def test_boot_payload_includes_role_bound_suggested_prompts(self):
		with (
			patch.object(
				api,
				"get_settings",
				return_value=self.make_settings(
					suggested_prompts=[
						SimpleNamespace(
							enabled=1,
							role="Purchase User",
							group_label="采购",
							prompt="查看逾期采购订单",
						),
						SimpleNamespace(
							enabled=0,
							role="HR User",
							group_label="人力资源",
							prompt="今天谁请假",
						),
						SimpleNamespace(
							enabled=1,
							role="",
							group_label="制造",
							prompt="无角色提示",
						),
					],
				),
			),
			patch.object(api, "can_access_ask_alyf", return_value=True),
			patch.object(api.frappe.db, "exists", return_value=True),
		):
			payload = api.get_ask_alyf_boot_payload()

		self.assertEqual(
			payload["suggested_prompts"],
			[
				{
					"role": "Purchase User",
					"group": "采购",
					"text": "查看逾期采购订单",
				}
			],
		)
		self.assertTrue(payload["suggested_prompts_configured"])

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

	def test_boot_payload_respects_explicit_disabled_panel_switch_single_values(self):
		def get_value(doctype, filters, fieldname=None):
			if doctype == "Singles" and filters.get("field") in {
				"show_file_upload_button",
				"show_voice_input_button",
			}:
				return "0"
			return None

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
			patch.object(api.frappe.db, "get_value", side_effect=get_value),
			patch.object(api.frappe.db, "exists", return_value=True),
		):
			payload = api.get_ask_alyf_boot_payload()

		self.assertFalse(payload["panel_config"]["show_file_upload_button"])
		self.assertFalse(payload["panel_config"]["show_voice_input_button"])
		self.assertFalse(payload["file_upload_enabled"])
		self.assertFalse(payload["voice_input_enabled"])

	def test_boot_payload_uses_default_panel_switches_when_single_values_are_missing(self):
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
			patch.object(api.frappe.db, "get_value", return_value=None),
			patch.object(api.frappe.db, "exists", return_value=True),
		):
			payload = api.get_ask_alyf_boot_payload()

		self.assertTrue(payload["panel_config"]["show_file_upload_button"])
		self.assertTrue(payload["panel_config"]["show_voice_input_button"])
		self.assertTrue(payload["file_upload_enabled"])
		self.assertTrue(payload["voice_input_enabled"])

	def test_list_conversations_excludes_empty_conversations(self):
		with (
			patch.object(api, "can_access_ask_alyf", return_value=True),
			patch.object(api.frappe, "get_list", return_value=[]) as get_list,
			patch.dict(api.frappe.session, {"user": "user@example.com"}),
		):
			api.list_conversations()

		self.assertEqual(
			get_list.call_args.kwargs["filters"],
			{
				"owner": "user@example.com",
				"last_message_at": ["is", "set"],
			},
		)

	def test_start_new_conversation_reuses_existing_empty_conversation(self):
		empty_conversation = self.make_conversation_doc(name="EMPTY-1")
		new_conversation = self.make_conversation_doc(name="NEW-1")

		def get_doc(*args, **kwargs):
			if args == ("Ask ALYF Conversation", "EMPTY-1"):
				return empty_conversation
			return new_conversation

		with (
			patch.object(api, "can_access_ask_alyf", return_value=True),
			patch.object(
				api.frappe,
				"get_list",
				return_value=[SimpleNamespace(name="EMPTY-1")],
			),
			patch.object(api.frappe, "get_doc", side_effect=get_doc),
			patch.dict(api.frappe.session, {"user": "user@example.com"}),
		):
			payload = api.start_new_conversation()

		self.assertEqual(payload["name"], "EMPTY-1")
		new_conversation.insert.assert_not_called()

	def test_normalize_file_attachments_returns_file_metadata(self):
		file_doc = SimpleNamespace(
			name="FILE-1",
			file_name="invoice.png",
			file_url="/files/invoice.png",
			file_type="PNG",
			file_size=1536,
			check_permission=lambda permission: None,
		)

		with (
			patch.object(api.frappe.db, "exists", return_value=True),
			patch.object(api.frappe, "get_doc", return_value=file_doc),
		):
			files = api.normalize_file_attachments([{"name": "FILE-1"}])

		self.assertEqual(
			files,
			[
				{
					"name": "FILE-1",
					"file_name": "invoice.png",
					"file_url": "/files/invoice.png",
					"file_type": "PNG",
					"file_size": 1536,
				}
			],
		)

	def test_send_message_stores_files_on_user_message_without_extra_system_message(self):
		conversation = SimpleNamespace(
			name="CONV-1",
			title="New Conversation",
			route="",
			messages_json="[]",
			pending_operation_json="",
			last_context_json="",
			save=lambda: None,
		)
		file_entry = {
			"name": "FILE-1",
			"file_name": "invoice.png",
			"file_url": "/files/invoice.png",
		}

		with (
			patch.object(api, "can_access_ask_alyf", return_value=True),
			patch.object(api, "get_or_create_conversation", return_value=conversation),
			patch.object(api, "normalize_file_attachments", return_value=[file_entry]),
			patch.object(api, "enqueue"),
		):
			api.send_message(
				"请分析附件",
				conversation="CONV-1",
				files=[{"name": "FILE-1"}],
			)

		messages = api.loads(conversation.messages_json, [])
		self.assertEqual(len(messages), 1)
		self.assertEqual(messages[0]["role"], "user")
		self.assertEqual(messages[0]["content"], "请分析附件")
		self.assertEqual(messages[0]["metadata"]["files"], [file_entry])

	def test_process_message_job_passes_current_file_metadata_to_agent(self):
		file_entry = {
			"name": "FILE-1",
			"file_name": "invoice.png",
			"file_url": "/files/invoice.png",
		}
		user_message = api.make_message("user", "请分析附件", mode=api.MODE_ASK, files=[file_entry])
		conversation = SimpleNamespace(
			name="CONV-1",
			owner="test@example.com",
			messages_json=api.dumps([user_message]),
			pending_operation_json="",
			save=lambda: None,
		)

		with (
			patch.object(api.frappe, "get_doc", return_value=conversation),
			patch.object(api.frappe, "publish_realtime"),
			patch.object(
				api,
				"run_message",
				return_value={
					"response": "已收到附件。",
					"pending_operations": [],
					"document_extractions": [],
					"attached_files": [],
				},
			) as run_message,
		):
			api.process_message_job(
				conversation_name="CONV-1",
				message="请分析附件",
				mode=api.MODE_ASK,
				context_data={},
				user_message_id=user_message["id"],
			)

		agent_message = run_message.call_args.kwargs["message"]
		self.assertIn("请分析附件", agent_message)
		self.assertIn("Attachment metadata: id=FILE-1, name=invoice.png", agent_message)
		self.assertEqual(run_message.call_args.kwargs["conversation_history"], [])
