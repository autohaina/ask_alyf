(function (root, factory) {
	const api = factory();
	if (typeof module === "object" && module.exports) {
		module.exports = api;
	}
	root.askAlyfSuggestedPrompts = api;
})(typeof window !== "undefined" ? window : globalThis, function () {
	function shuffleArray(array, random = Math.random) {
		const shuffled = [...array];
		for (let i = shuffled.length - 1; i > 0; i--) {
			const j = Math.floor(random() * (i + 1));
			[shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
		}
		return shuffled;
	}

	function normalizeText(value) {
		return (value || "").toString().trim();
	}

	function groupConfiguredPrompts(configuredPrompts, userRoles) {
		const grouped = new Map();
		if (!Array.isArray(configuredPrompts)) {
			return [];
		}

		for (const prompt of configuredPrompts) {
			const role = normalizeText(prompt?.role);
			const group = normalizeText(prompt?.group);
			const text = normalizeText(prompt?.text);
			if (!role || !group || !text || !userRoles.has(role)) {
				continue;
			}
			if (!grouped.has(group)) {
				grouped.set(group, []);
			}
			grouped.get(group).push(text);
		}

		return Array.from(grouped, ([label, prompts]) => ({ label, prompts }));
	}

	function selectPromptGroups(groups, options = {}) {
		const groupLimit = options.groupLimit ?? 2;
		const promptsPerGroup = options.promptsPerGroup ?? 3;
		const random = options.random || Math.random;
		const normalizedGroups = (Array.isArray(groups) ? groups : [])
			.map((group) => ({
				label: normalizeText(group?.label),
				prompts: (Array.isArray(group?.prompts) ? group.prompts : [])
					.map(normalizeText)
					.filter(Boolean),
			}))
			.filter((group) => group.label && group.prompts.length);

		return shuffleArray(normalizedGroups, random)
			.slice(0, groupLimit)
			.flatMap((group) =>
				shuffleArray(group.prompts, random)
					.slice(0, promptsPerGroup)
					.map((text) => ({ group: group.label, text })),
			);
	}

	return {
		groupConfiguredPrompts,
		selectPromptGroups,
		shuffleArray,
	};
});
