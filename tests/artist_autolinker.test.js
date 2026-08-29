const assert = require("node:assert/strict");
const fs = require("node:fs");
const test = require("node:test");
const vm = require("node:vm");

class Element {
  constructor(tagName, options = {}) {
    this.tagName = tagName.toLowerCase();
    this.classes = new Set(options.classes || []);
    this.attributes = options.attributes || {};
    this.parentElement = options.parent || null;
    this.children = [];
    this.className = "";
    this.href = "";
    this.textContent = "";
  }

  closest(selectorList) {
    for (let element = this; element; element = element.parentElement) {
      if (selectorList.split(",").some((selector) => element.matches(selector.trim()))) return element;
    }
    return null;
  }

  matches(selector) {
    if (!selector) return false;
    if (selector.startsWith(".")) return this.classes.has(selector.slice(1));
    const attribute = selector.match(/^\[([^=\]]+)(?:=['"]?([^'"\]]+)['"]?)?\]$/);
    if (attribute) {
      if (!(attribute[1] in this.attributes)) return false;
      return attribute[2] === undefined || this.attributes[attribute[1]] === attribute[2];
    }
    return this.tagName === selector.toLowerCase();
  }

  append(node) {
    this.children.push(node);
  }
}

class TextNode {
  constructor(value, parentElement) {
    this.nodeValue = value;
    this.parentElement = parentElement;
    this.replacement = null;
  }

  replaceWith(fragment) {
    this.replacement = fragment.children;
  }
}

function linkedText(node) {
  return (node.replacement || []).filter((item) => item instanceof Element && item.tagName === "a");
}

test("Blogger Blog widget article is linked while sidebar and protected content are untouched", () => {
  const blogWidget = new Element("div", {classes: ["widget", "Blog"]});
  const postBody = new Element("div", {classes: ["post-body"], parent: blogWidget});
  const paragraph = new Element("p", {parent: postBody});
  const articleText = new TextNode("Sparks played in Paris.", paragraph);
  const secondParagraph = new Element("p", {parent: postBody});
  const secondOccurrence = new TextNode("Sparks returned for an encore.", secondParagraph);
  const ordinaryProse = new TextNode("The lights went down before the show.", secondParagraph);
  const aliasProse = new TextNode("QOTSA closed the festival.", secondParagraph);

  const existingAnchor = new Element("a", {parent: postBody});
  const anchorText = new TextNode("Sparks existing link", existingAnchor);
  const ad = new Element("ins", {classes: ["adsbygoogle"], parent: postBody});
  const adText = new TextNode("Sparks advertisement", ad);
  const embed = new Element("iframe", {parent: postBody});
  const embedText = new TextNode("Sparks embed", embed);
  const optOut = new Element("p", {attributes: {"data-ee-no-autolink": ""}, parent: postBody});
  const optOutText = new TextNode("Sparks opted out", optOut);

  postBody.textNodes = [articleText, secondOccurrence, ordinaryProse, aliasProse, anchorText, adText, embedText, optOutText];

  const sidebarWidget = new Element("aside", {classes: ["widget"]});
  const sidebarText = new TextNode("Sparks sidebar item", sidebarWidget);
  sidebarWidget.textNodes = [sidebarText];

  const document = {
    documentElement: {dataset: {}},
    readyState: "complete",
    querySelectorAll(selector) {
      assert.equal(selector, ".post-body, .entry-content");
      return [postBody];
    },
    createTreeWalker(root) {
      let index = 0;
      return {nextNode: () => root.textNodes[index++] || null};
    },
    createDocumentFragment() {
      return {children: [], append(node) { this.children.push(node); }};
    },
    createTextNode(value) {
      return new TextNode(value, null);
    },
    createElement(tagName) {
      return new Element(tagName);
    },
    addEventListener() {},
  };
  const window = {
    ElectricEyeArtistLookup: {
      artistPage: "https://example.test/artist.html?artist=",
      proseAutolinkExclusions: ["down"],
      terms: {Sparks: "sparks", Down: "down", QOTSA: "queens-of-the-stone-age"},
    },
  };
  const source = fs.readFileSync("concert_calendar/static/artist-autolinker.js", "utf8");

  vm.runInNewContext(source, {window, document, NodeFilter: {SHOW_TEXT: 4}, Set, Object, RegExp, encodeURIComponent});

  const links = linkedText(articleText);
  assert.equal(links.length, 1);
  assert.equal(links[0].textContent, "Sparks");
  assert.equal(links[0].href, "https://example.test/artist.html?artist=sparks/");
  assert.equal(linkedText(secondOccurrence).length, 0, "only the first occurrence is linked by default");
  assert.equal(linkedText(ordinaryProse).length, 0, "ordinary down prose is not linked to Down");
  assert.equal(linkedText(aliasProse)[0].href, "https://example.test/artist.html?artist=queens-of-the-stone-age/");
  assert.equal(anchorText.replacement, null, "existing anchor is untouched");
  assert.equal(adText.replacement, null, "ad is untouched");
  assert.equal(embedText.replacement, null, "embed is untouched");
  assert.equal(optOutText.replacement, null, "explicit opt-out is untouched");
  assert.equal(sidebarText.replacement, null, "sidebar widget outside the article root is untouched");
});
