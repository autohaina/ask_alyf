const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const source = fs.readFileSync(path.join(__dirname, "ask_alyf.bundle.js"), "utf8");

test("bootstrap and new chat both reset suggested prompt cache before applying a conversation", () => {
	const bootstrap = source.slice(source.indexOf("async loadBootstrap()"), source.indexOf("async ensureDoctypeMeta"));
	const newConversation = source.slice(
		source.indexOf("async startNewConversation()"),
		source.indexOf("isFrontendAction", source.indexOf("async startNewConversation()")),
	);
	assert.match(bootstrap, /resetSuggestedPromptCache\(\)[\s\S]*applyConversation/);
	assert.match(newConversation, /resetSuggestedPromptCache\(\)[\s\S]*applyConversation/);
});
