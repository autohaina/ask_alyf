const assert = require("node:assert/strict");
const test = require("node:test");

const {
	selectPromptGroups,
	groupConfiguredPrompts,
} = require("./suggested_prompts");

function sequenceRandom(values) {
	let index = 0;
	return () => values[index++ % values.length];
}

test("selectPromptGroups chooses two random groups and three random prompts per group", () => {
	const groups = [
		{ label: "Sales", prompts: ["S1", "S2", "S3", "S4"] },
		{ label: "Stock", prompts: ["T1", "T2", "T3", "T4"] },
		{ label: "System", prompts: ["Y1", "Y2", "Y3", "Y4"] },
	];

	const prompts = selectPromptGroups(groups, {
		groupLimit: 2,
		promptsPerGroup: 3,
		random: sequenceRandom([0.1, 0.9, 0.2, 0.8, 0.3, 0.7, 0.4]),
	});

	assert.deepEqual(prompts, [
		{ group: "System", text: "Y2" },
		{ group: "System", text: "Y4" },
		{ group: "System", text: "Y3" },
		{ group: "Stock", text: "T4" },
		{ group: "Stock", text: "T1" },
		{ group: "Stock", text: "T2" },
	]);
	assert.equal(new Set(prompts.map((prompt) => prompt.group)).size, 2);
	assert.equal(prompts.length, 6);
});

test("groupConfiguredPrompts only includes prompts for current user roles", () => {
	const groups = groupConfiguredPrompts(
		[
			{ role: "System Manager", group: "System", text: "Check errors" },
			{ role: "Sales User", group: "Sales", text: "Sales today" },
			{ role: "Guest", group: "Guest", text: "Hidden" },
			{ role: "System Manager", group: "System", text: "Who logged in today?" },
			{ role: "Sales User", group: "Sales", text: "Open leads" },
			{ role: "Sales User", group: "Sales", text: "" },
		],
		new Set(["System Manager", "Sales User"]),
	);

	assert.deepEqual(groups, [
		{
			label: "System",
			prompts: ["Check errors", "Who logged in today?"],
		},
		{
			label: "Sales",
			prompts: ["Sales today", "Open leads"],
		},
	]);
});
