const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const { test } = require("node:test");
const vm = require("node:vm");

// Small DOM double for exercising the real signup and card-rendering code.
class Element {
  constructor() {
    this.children = [];
    this.options = [{}];
    this.value = "";
    this.listeners = {};
    this.classList = { add() {}, remove() {} };
  }

  set innerHTML(value) {
    this.html = value;
    this.children = [];
  }

  appendChild(child) {
    this.children.push(child);
  }

  setAttribute() {}

  addEventListener(event, callback) {
    this.listeners[event] = callback;
  }
}

test("signup refreshes participants and availability without a page reload", async () => {
  const elements = Object.fromEntries(
    ["activities-list", "activity", "signup-form", "message", "email"].map(
      (id) => [id, new Element()]
    )
  );
  elements.activity.options = elements.activity.children;
  elements.activity.options.push({ value: "" });
  elements["signup-form"].reset = () => {
    elements.email.value = "";
    elements.activity.value = "";
  };
  const participants = [];
  const requests = [];
  const context = {
    document: {
      getElementById: (id) => elements[id],
      createElement: () => new Element(),
      addEventListener: (_event, callback) => callback(),
    },
    fetch: async (url, options = {}) => {
      requests.push({ url, options });
      if (options.method === "POST") {
        participants.push(new URL(url, "http://localhost").searchParams.get("email"));
        return { ok: true, json: async () => ({ message: "Signed up" }) };
      }
      return {
        ok: true,
        json: async () => ({
          "Chess Club": {
            description: "Play chess",
            schedule: "Fridays",
            max_participants: 12,
            participants: [...participants],
          },
        }),
      };
    },
    setTimeout() {},
    console,
  };
  vm.runInNewContext(
    readFileSync(require.resolve("../src/static/app.js"), "utf8"), context
  );
  await new Promise(setImmediate);
  assert.match(elements["activities-list"].children[0].html, /12 spots left/);

  elements.email.value = "student@mergington.edu";
  elements.activity.value = "Chess Club";
  await elements["signup-form"].listeners.submit({ preventDefault() {} });

  const cards = elements["activities-list"].children;
  assert.equal(cards.length, 1);
  assert.match(cards[0].html, /11 spots left/);
  const section = cards[0].children[0];
  assert.equal(section.children[0].textContent, "Participants (1)");
  assert.equal(section.children[1].children[0].children[0].textContent, "student@mergington.edu");
  assert.equal(elements.activity.options.length, 2, "Dropdown options must not duplicate");
  const activityRequests = requests.filter(({ url }) => url === "/activities");
  assert.equal(activityRequests.length, 2);
  assert.ok(activityRequests.every(({ options }) => options.cache === "no-store"));
});