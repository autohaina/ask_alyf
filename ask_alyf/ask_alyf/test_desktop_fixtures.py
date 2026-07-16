import json
from pathlib import Path

from frappe.tests import UnitTestCase


APP_ROOT = Path(__file__).resolve().parents[1]


class UnitTestDesktopFixtures(UnitTestCase):
	def test_workspace_sidebar_desktop_icon_label_has_matching_sidebar(self):
		desktop_icon_path = APP_ROOT / "desktop_icon" / "ask_alyf.json"
		desktop_icon = json.loads(desktop_icon_path.read_text())

		sidebar_names = {
			json.loads(path.read_text()).get("name")
			for path in (APP_ROOT / "workspace_sidebar").glob("*.json")
		}

		self.assertEqual(desktop_icon["link_type"], "Workspace Sidebar")
		self.assertIn(desktop_icon["label"], sidebar_names)
