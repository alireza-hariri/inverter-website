/*
 * The classic WordPress editor: a Visual tab (contenteditable with a toolbar)
 * and an HTML tab (the original textarea), kept in sync.
 *
 * The textarea stays the source of truth -- it is what the form posts -- so
 * every visual edit is copied back into it and announced with an `input`
 * event, which is how seo-box.js re-scores the body as the editor types. The
 * backend sanitizes whatever arrives (apps/content/richtext.py), so this
 * editor only has to produce reasonable markup, not safe markup.
 */
(function () {
  "use strict";

  const BLOCKS = [["p", "Paragraph"], ["h2", "Heading 2"], ["h3", "Heading 3"], ["h4", "Heading 4"], ["blockquote", "Quote"]];

  function escapeHtml(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  // Same rule as richtext.render: text with no tags is a series of paragraphs.
  function toHtml(value) {
    if (/<\s*[a-zA-Z][^>]*>/.test(value)) return value;
    return value.split(/\n\s*\n/).map((b) => b.trim()).filter(Boolean)
      .map((b) => "<p>" + escapeHtml(b).replace(/\n/g, "<br>") + "</p>").join("");
  }

  function words(text) {
    return (text.trim().match(/\S+/g) || []).length;
  }

  function enhance(textarea) {
    const dir = textarea.dataset.dir || "rtl";
    const wrap = document.createElement("div");
    wrap.className = "wp-rte";
    const bar = document.createElement("div");
    bar.className = "wp-rte__bar";
    const visual = document.createElement("div");
    visual.className = "wp-rte__visual";
    visual.contentEditable = "true";
    visual.dir = dir;
    visual.setAttribute("role", "textbox");
    visual.setAttribute("aria-multiline", "true");
    const status = document.createElement("div");
    status.className = "wp-rte__status";
    textarea.parentNode.insertBefore(wrap, textarea);
    wrap.append(bar, visual, textarea, status);
    textarea.dir = "ltr";

    let mode = "visual";

    function sync() {
      if (mode !== "visual") return;
      let html = visual.innerHTML.replace(/<p><br><\/p>$/i, "").replace(/^<br>$/i, "");
      textarea.value = html;
      textarea.dispatchEvent(new Event("input", { bubbles: true }));
      count();
    }
    function count() {
      const text = mode === "visual" ? visual.innerText : textarea.value.replace(/<[^>]+>/g, " ");
      status.replaceChildren(
        Object.assign(document.createElement("span"), { textContent: "Word count: " + words(text) }),
        Object.assign(document.createElement("span"), { textContent: mode === "visual" ? "Visual" : "HTML" }),
      );
    }
    function exec(cmd, value) {
      visual.focus();
      document.execCommand(cmd, false, value);
      sync();
    }
    function button(label, title, handler) {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "wp-rte__btn";
      b.innerHTML = label;
      b.title = title;
      b.addEventListener("mousedown", (e) => e.preventDefault());
      b.addEventListener("click", handler);
      bar.append(b);
      return b;
    }
    function sep() {
      bar.append(Object.assign(document.createElement("span"), { className: "wp-rte__sep" }));
    }

    const block = document.createElement("select");
    block.title = "Paragraph format";
    for (const [tag, label] of BLOCKS) block.append(new Option(label, tag));
    block.addEventListener("change", () => exec("formatBlock", "<" + block.value + ">"));
    bar.append(block);
    sep();
    button("<b>B</b>", "Bold (Ctrl+B)", () => exec("bold"));
    button("<i>I</i>", "Italic (Ctrl+I)", () => exec("italic"));
    button("•≡", "Bulleted list", () => exec("insertUnorderedList"));
    button("1≡", "Numbered list", () => exec("insertOrderedList"));
    button("❝", "Blockquote", () => exec("formatBlock", "<blockquote>"));
    sep();
    button("🔗", "Insert link (Ctrl+K) — use /fa/services/… for internal links", link);
    button("⛓̸", "Remove link", () => exec("unlink"));
    button("🖼", "Add media", () => window.WpMedia && window.WpMedia.open((item) => {
      exec("insertHTML", '<img src="' + item.url.replace(/"/g, "&quot;") + '" alt="' + escapeHtml(item.alt || "").replace(/"/g, "&quot;") + '" loading="lazy">');
    }));
    button("▦", "Insert table", () => exec("insertHTML",
      "<table><thead><tr><th>…</th><th>…</th></tr></thead><tbody><tr><td>…</td><td>…</td></tr></tbody></table><p><br></p>"));
    button("―", "Horizontal line", () => exec("insertHorizontalRule"));
    button("⌫", "Clear formatting", () => exec("removeFormat"));

    function link() {
      const url = prompt("Link URL (internal: /fa/services/elevator-inverter-repair)", "https://");
      if (url && url !== "https://") exec("createLink", url);
    }

    const tabs = document.createElement("div");
    tabs.className = "wp-rte__tabs";
    const tVisual = Object.assign(document.createElement("button"), { type: "button", textContent: "Visual", className: "is-active" });
    const tHtml = Object.assign(document.createElement("button"), { type: "button", textContent: "HTML" });
    tabs.append(tVisual, tHtml);
    bar.append(tabs);

    function setMode(next) {
      if (next === mode) return;
      if (next === "html") {
        sync();
        mode = "html";
        visual.hidden = true;
        textarea.hidden = false;
        bar.querySelectorAll(".wp-rte__btn, select").forEach((b) => (b.disabled = true));
      } else {
        mode = "visual";
        visual.innerHTML = toHtml(textarea.value);
        visual.hidden = false;
        textarea.hidden = true;
        bar.querySelectorAll(".wp-rte__btn, select").forEach((b) => (b.disabled = false));
      }
      tVisual.classList.toggle("is-active", mode === "visual");
      tHtml.classList.toggle("is-active", mode === "html");
      count();
    }
    tVisual.addEventListener("click", () => setMode("visual"));
    tHtml.addEventListener("click", () => setMode("html"));

    visual.innerHTML = toHtml(textarea.value);
    textarea.hidden = true;
    visual.addEventListener("input", sync);
    visual.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") { e.preventDefault(); link(); }
    });
    // Reflect the block format under the caret in the dropdown.
    document.addEventListener("selectionchange", () => {
      if (mode !== "visual" || !visual.contains(document.getSelection().anchorNode)) return;
      const value = (document.queryCommandValue("formatBlock") || "p").toLowerCase().replace(/[<>]/g, "");
      block.value = BLOCKS.some(([t]) => t === value) ? value : "p";
    });
    textarea.addEventListener("input", (e) => { if (mode === "html" && e.isTrusted) count(); });
    textarea.form && textarea.form.addEventListener("submit", sync);
    count();
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.execCommand("defaultParagraphSeparator", false, "p");
    document.querySelectorAll("textarea.wp-richtext").forEach(enhance);
  });
})();
