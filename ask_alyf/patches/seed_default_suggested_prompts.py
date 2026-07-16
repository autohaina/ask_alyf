import frappe


DEFAULT_SUGGESTED_PROMPTS = [
	("Sales User", "销售", "绘制过去 6 个月每月销售收入图表"),
	("Sales User", "销售", "哪些销售订单待发货？"),
	("Sales User", "销售", "本月发送了多少报价单？"),
	("Sales Manager", "销售", "绘制过去 6 个月每月销售收入图表"),
	("Sales Manager", "销售", "哪些销售订单待发货？"),
	("Sales Manager", "销售", "本月发送了多少报价单？"),
	("Purchase User", "采购", "绘制本季度按供应商划分的支出图表"),
	("Purchase User", "采购", "哪些采购订单已逾期？"),
	("Purchase User", "采购", "我有多少待处理的采购收据？"),
	("Purchase Manager", "采购", "绘制本季度按供应商划分的支出图表"),
	("Purchase Manager", "采购", "哪些采购订单已逾期？"),
	("Purchase Manager", "采购", "我有多少待处理的采购收据？"),
	("Accounts User", "会计", "绘制按成本中心划分的月度费用图表"),
	("Accounts User", "会计", "显示超过 30 天未付款的销售发票"),
	("Accounts User", "会计", "未收账款总额是多少？"),
	("Accounts Manager", "会计", "绘制按成本中心划分的月度费用图表"),
	("Accounts Manager", "会计", "显示超过 30 天未付款的销售发票"),
	("Accounts Manager", "会计", "未收账款总额是多少？"),
	("HR User", "人力资源", "按部门绘制员工人数图表"),
	("HR User", "人力资源", "今天哪些员工休假？"),
	("HR User", "人力资源", "有多少请假申请待批准？"),
	("HR Manager", "人力资源", "按部门绘制员工人数图表"),
	("HR Manager", "人力资源", "今天哪些员工休假？"),
	("HR Manager", "人力资源", "有多少请假申请待批准？"),
	("Stock User", "库存", "按仓库绘制库存价值图表"),
	("Stock User", "库存", "哪些项目低于其再订货水平？"),
	("Stock User", "库存", "本月移动最多的前 10 个项目是什么？"),
	("Stock Manager", "库存", "按仓库绘制库存价值图表"),
	("Stock Manager", "库存", "哪些项目低于其再订货水平？"),
	("Stock Manager", "库存", "本月移动最多的前 10 个项目是什么？"),
	("Manufacturing User", "制造", "绘制本周按项目划分的生产产量图表"),
	("Manufacturing User", "制造", "显示未完成工单及其状态"),
	("Manufacturing User", "制造", "有多少工单落后于计划？"),
	("Manufacturing Manager", "制造", "绘制本周按项目划分的生产产量图表"),
	("Manufacturing Manager", "制造", "显示未完成工单及其状态"),
	("Manufacturing Manager", "制造", "有多少工单落后于计划？"),
	("Projects User", "项目", "以图表显示项目进度"),
	("Projects User", "项目", "分配给我的未完成任务有哪些？"),
	("Projects User", "项目", "哪些项目任务已逾期？"),
	("Projects Manager", "项目", "以图表显示项目进度"),
	("Projects Manager", "项目", "分配给我的未完成任务有哪些？"),
	("Projects Manager", "项目", "哪些项目任务已逾期？"),
	("Support Team", "支持", "按优先级绘制未解决问题图表"),
	("Support Team", "支持", "显示本周未解决的问题"),
	("Support Team", "支持", "问题的平均解决时间是多少？"),
	("System Manager", "系统", "显示记录数最多的前 10 个 DocType"),
	("System Manager", "系统", "最近有哪些错误日志？"),
	("System Manager", "系统", "今天哪些用户登录了？"),
]


def execute():
	if not frappe.db.exists("DocType", "Ask ALYF Settings"):
		return

	settings = frappe.get_single("Ask ALYF Settings")
	if settings.get("suggested_prompts"):
		return

	for role, group_label, prompt in DEFAULT_SUGGESTED_PROMPTS:
		if not frappe.db.exists("Role", role):
			continue
		settings.append(
			"suggested_prompts",
			{
				"enabled": 1,
				"role": role,
				"group_label": group_label,
				"prompt": prompt,
			},
		)

	if settings.get("suggested_prompts"):
		settings.flags.ignore_permissions = True
		settings.save()
