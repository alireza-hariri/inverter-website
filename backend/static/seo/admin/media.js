/*
 * The WordPress media modal, in miniature: browse and upload images, pick one.
 *
 * `WpMedia.open(onSelect)` shows the modal and calls `onSelect({url, alt, title})`.
 * Every input.wp-image-url also gets a preview and a "Choose image" button.
 * Uploads go to MediaFileAdmin's upload view (apps/seo/admin.py), which needs
 * the admin's CSRF token.
 */
(function () {
  "use strict";

  const adminRoot = (() => {
    const parts = location.pathname.split("/");
    const i = parts.indexOf("admin");
    return (i >= 0 ? parts.slice(0, i + 1).join("/") : "/admin") + "/";
  })();
  const BROWSE = adminRoot + "seo/mediafile/browse/";
  const UPLOAD = adminRoot + "seo/mediafile/upload/";

  function csrfToken() {
    const input = document.querySelector("input[name=csrfmiddlewaretoken]");
    if (input) return input.value;
    const m = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : "";
  }

  function el(tag, attrs, children) {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (k === "text") node.textContent = v;
      else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
      else node.setAttribute(k, v);
    }
    for (const c of children || []) node.append(c);
    return node;
  }

  function open(onSelect) {
    let selected = null;
    const backdrop = el("div", { class: "wp-modal__backdrop" });
    const grid = el("div", { class: "wp-modal__grid" });
    const search = el("input", { type: "search", class: "wp-modal__search", placeholder: "Search media…" });
    const error = el("span", { class: "wp-modal__error" });
    const alt = el("input", { type: "text", placeholder: "Alt text (describe the image for search engines)" });
    const choose = el("button", { type: "button", class: "button default", disabled: "disabled", text: "Select" });
    const fileInput = el("input", { type: "file", accept: "image/*", multiple: "multiple", hidden: "hidden" });
    const drop = el("div", { class: "wp-modal__drop" }, [
      el("p", { text: "Drop files to upload" }),
      el("p", { text: "or" }),
      el("button", { type: "button", class: "button", text: "Select files", onclick: () => fileInput.click() }),
      fileInput,
    ]);
    const libraryPane = el("div", {}, [search, grid]);
    const uploadPane = el("div", { hidden: "hidden" }, [drop]);
    const tabUpload = el("button", { type: "button", text: "Upload files" });
    const tabLibrary = el("button", { type: "button", class: "is-active", text: "Media Library" });
    const modal = el("div", { class: "wp-modal", role: "dialog", "aria-modal": "true", "aria-label": "Media library" }, [
      el("div", { class: "wp-modal__head" }, [
        el("h2", { text: "Select image" }),
        el("button", { type: "button", class: "wp-modal__close", "aria-label": "Close", text: "×", onclick: close }),
      ]),
      el("div", { class: "wp-modal__tabs" }, [tabUpload, tabLibrary]),
      el("div", { class: "wp-modal__body" }, [uploadPane, libraryPane]),
      el("div", { class: "wp-modal__foot" }, [error, alt, choose]),
    ]);

    function showTab(upload) {
      uploadPane.hidden = !upload;
      libraryPane.hidden = upload;
      tabUpload.classList.toggle("is-active", upload);
      tabLibrary.classList.toggle("is-active", !upload);
    }
    tabUpload.addEventListener("click", () => showTab(true));
    tabLibrary.addEventListener("click", () => showTab(false));

    function select(item, button) {
      selected = item;
      grid.querySelectorAll(".is-selected").forEach((b) => b.classList.remove("is-selected"));
      if (button) button.classList.add("is-selected");
      alt.value = item.alt || "";
      choose.disabled = false;
    }

    function render(items) {
      grid.replaceChildren(...items.map((item) => {
        const button = el("button", { type: "button", class: "wp-modal__item", title: item.title }, [
          el("img", { src: item.url, alt: item.alt || "", loading: "lazy" }),
        ]);
        button.addEventListener("click", () => select(item, button));
        button.addEventListener("dblclick", () => { select(item, button); finish(); });
        return button;
      }));
      if (!items.length) grid.append(el("p", { text: "No images yet — upload one." }));
    }

    async function load() {
      try {
        const res = await fetch(BROWSE + "?q=" + encodeURIComponent(search.value), { credentials: "same-origin" });
        render((await res.json()).results || []);
      } catch (e) {
        error.textContent = "Could not load the media library.";
      }
    }

    async function upload(files) {
      error.textContent = "";
      let last = null;
      for (const file of files) {
        const body = new FormData();
        body.append("file", file);
        try {
          const res = await fetch(UPLOAD, {
            method: "POST", body, credentials: "same-origin", headers: { "X-CSRFToken": csrfToken() },
          });
          const data = await res.json();
          if (!res.ok) throw new Error(data.error || "Upload failed");
          last = data;
        } catch (e) {
          error.textContent = file.name + ": " + e.message;
        }
      }
      showTab(false);
      await load();
      if (last) select(last, grid.querySelector(".wp-modal__item"));
    }

    function finish() {
      if (!selected) return;
      onSelect({ ...selected, alt: alt.value });
      close();
    }

    function close() {
      backdrop.remove();
      modal.remove();
      document.removeEventListener("keydown", onKey);
    }
    function onKey(e) { if (e.key === "Escape") close(); }

    let timer;
    search.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(load, 250); });
    fileInput.addEventListener("change", () => upload(fileInput.files));
    drop.addEventListener("dragover", (e) => { e.preventDefault(); drop.classList.add("is-over"); });
    drop.addEventListener("dragleave", () => drop.classList.remove("is-over"));
    drop.addEventListener("drop", (e) => { e.preventDefault(); drop.classList.remove("is-over"); upload(e.dataTransfer.files); });
    choose.addEventListener("click", finish);
    document.addEventListener("keydown", onKey);
    document.body.append(backdrop, modal);
    load();
  }

  function enhanceImageInput(input) {
    if (input.dataset.wpEnhanced) return;
    input.dataset.wpEnhanced = "1";
    const preview = el("img", { class: "wp-image__preview", alt: "" });
    const chooseBtn = el("button", { type: "button", class: "button", text: "Choose image" });
    const removeBtn = el("button", { type: "button", class: "wp-image__remove", text: "Remove" });
    const wrap = el("div", { class: "wp-image" });
    input.replaceWith(wrap);
    wrap.append(preview, input, el("div", { class: "wp-image__actions" }, [chooseBtn, removeBtn]));

    function refresh() {
      const url = input.value.trim();
      preview.hidden = !url;
      removeBtn.hidden = !url;
      if (url) preview.src = url;
      chooseBtn.textContent = url ? "Replace image" : "Choose image";
    }
    chooseBtn.addEventListener("click", () => open((item) => {
      input.value = item.url;
      input.dispatchEvent(new Event("input", { bubbles: true }));
      // Fill the record's alt-text field too when it is empty, as WP does.
      const altField = document.querySelector("#id_image_alt_fa");
      if (altField && !altField.value && item.alt) {
        altField.value = item.alt;
        altField.dispatchEvent(new Event("input", { bubbles: true }));
      }
      refresh();
    }));
    removeBtn.addEventListener("click", () => {
      input.value = "";
      input.dispatchEvent(new Event("input", { bubbles: true }));
      refresh();
    });
    input.addEventListener("input", refresh);
    preview.addEventListener("error", () => { preview.hidden = true; });
    refresh();
  }

  window.WpMedia = { open };
  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("input.wp-image-url").forEach(enhanceImageInput);
  });
})();
