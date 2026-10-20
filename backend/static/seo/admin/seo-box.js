/*
 * The Yoast-style SEO box: turns each fieldset.wp-seo into a Google preview,
 * title/description length meters and a live checklist for its language.
 *
 * The checks mirror apps/seo/analysis.py, which scores saved records for the
 * list-view dots -- keep thresholds and rules identical in both files.
 * Configuration (site URL, route, separator, site names) comes from the
 * #seo-box-config script that templates/admin/wp_change_form.html writes.
 */
(function () {
  "use strict";

  const TITLE_MIN = 30, TITLE_MAX = 60, DESC_MIN = 120, DESC_MAX = 160;
  const FIELD_MAP = {
    service: { title: "title", intro: "summary", body: "body", image: "image", minWords: 300 },
    brand: { title: "name", intro: "description", body: "content", image: "logo", minWords: 200 },
    article: { title: "title", intro: "excerpt", body: "body", image: "image", minWords: 600 },
    pageseo: { title: null, intro: "intro", body: null, image: "og_image", minWords: 0 },
  };
  const LABELS = { good: "Good", ok: "OK", bad: "Problem" };

  function val(id) {
    const node = document.getElementById(id);
    return node ? node.value || "" : "";
  }
  function plain(html) {
    const div = document.createElement("div");
    div.innerHTML = html;
    return (div.textContent || "").replace(/\s+/g, " ").trim();
  }
  function has(text, phrase) {
    return !!phrase && text.toLowerCase().includes(phrase.toLowerCase());
  }
  function truncate(s, n) {
    return s.length > n ? s.slice(0, n - 1).trimEnd() + " …" : s;
  }
  function el(tag, cls, text) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  }
  function dot(status) {
    return el("span", "seo-dot seo-dot--" + status);
  }

  function analyse(cfg, map, lang) {
    const title = map.title ? val(`id_${map.title}_${lang}`) : "";
    const intro = map.intro ? val(`id_${map.intro}_${lang}`) : "";
    const body = map.body ? val(`id_${map.body}_${lang}`) : "";
    const seoTitle = effectiveTitle(cfg, map, lang);
    const desc = val(`id_seo_description_${lang}`);
    const kw = val(`id_focus_keyword_${lang}`).trim();
    const slug = val("id_slug");
    const text = plain(body);
    const wordCount = (text.match(/\S+/g) || []).length;
    const out = [];

    if (!kw) {
      out.push(["bad", "No focus keyphrase set. Enter the search phrase this page should rank for."]);
    } else {
      out.push([has(seoTitle, kw) ? "good" : "bad", "Keyphrase in SEO title."]);
      out.push([has(desc, kw) ? "good" : "bad", "Keyphrase in meta description."]);
      out.push([has((plain(intro) || text).slice(0, 400), kw) ? "good" : "ok", "Keyphrase in the introduction."]);
      if (map.body && wordCount) {
        const count = text.toLowerCase().split(kw.toLowerCase()).length - 1;
        const density = count * kw.split(/\s+/).length / wordCount * 100;
        out.push([density >= 0.5 && density <= 3 ? "good" : (count ? "ok" : "bad"),
          `Keyphrase density ${density.toFixed(1)}% — found ${count}× (aim for 0.5–3%).`]);
      }
      if (lang === "en" && map.body) {
        out.push([slug.includes(kw.toLowerCase().split(/\s+/).join("-")) ? "good" : "ok", "Keyphrase in the URL slug."]);
      }
    }
    let n = seoTitle.length;
    out.push([n >= TITLE_MIN && n <= TITLE_MAX ? "good" : (n ? "ok" : "bad"),
      `SEO title is ${n} characters (aim for ${TITLE_MIN}–${TITLE_MAX}).`]);
    n = desc.length;
    out.push([n >= DESC_MIN && n <= DESC_MAX ? "good" : (n ? "ok" : "bad"),
      `Meta description is ${n} characters (aim for ${DESC_MIN}–${DESC_MAX}).`]);
    if (map.body) {
      out.push([wordCount >= map.minWords ? "good" : (wordCount >= 100 ? "ok" : "bad"),
        `Body has ${wordCount} words (aim for ${map.minWords}+).`]);
      out.push([/<h2/i.test(body) ? "good" : "ok", "Body uses H2 subheadings."]);
      out.push([/href=["']\//i.test(body) ? "good" : "ok", "Body links to another page on this site (internal link)."]);
      const image = val(`id_${map.image}`) || val("id_og_image");
      if (image) out.push([val(`id_image_alt_${lang}`) ? "good" : "ok", "Main image has alt text."]);
      else out.push(["ok", "No image set."]);
    }
    return out;
  }

  function score(results) {
    if (!results.length) return "bad";
    if (results.some(([s, m]) => s === "bad" && m.startsWith("No focus"))) return "bad";
    const points = results.reduce((a, [s]) => a + ({ good: 1, ok: 0.5, bad: 0 })[s], 0) / results.length;
    return points >= 0.8 ? "good" : points >= 0.5 ? "ok" : "bad";
  }

  function effectiveTitle(cfg, map, lang) {
    const own = val(`id_seo_title_${lang}`).trim();
    if (own) return own;
    const site = (cfg.site_titles || {})[lang] || "";
    const title = map.title ? val(`id_${map.title}_${lang}`).trim() : "";
    return title ? (site ? `${title} ${cfg.separator || "|"} ${site}` : title) : site;
  }

  function meter(input, min, max) {
    const wrap = el("div");
    const bar = el("div", "seo-meter");
    const fill = el("span");
    bar.append(fill);
    const text = el("div", "seo-meter__text");
    wrap.append(bar, text);
    input.insertAdjacentElement("afterend", wrap);
    return (length) => {
      const pct = Math.min(100, (length / max) * 100);
      const status = length >= min && length <= max ? "good" : length > max ? "bad" : length ? "ok" : "bad";
      fill.style.width = pct + "%";
      fill.style.background = `var(--seo-${status})`;
      text.textContent = `${length} / ${max} characters` + (length > max ? " — too long, Google will cut it off" : length && length < min ? " — a little short" : "");
    };
  }

  function enhance(fieldset, cfg) {
    const kwInput = fieldset.querySelector("[id^=id_focus_keyword_]");
    if (!kwInput) return;
    const lang = kwInput.id.slice(-2);
    const map = FIELD_MAP[cfg.model] || FIELD_MAP.service;
    const dir = lang === "fa" ? "rtl" : "ltr";
    const titleInput = document.getElementById(`id_seo_title_${lang}`);
    const descInput = document.getElementById(`id_seo_description_${lang}`);

    // Google preview, at the top of the box.
    const box = el("div", "seo-box");
    const label = el("div", "seo-box__label", "Google preview");
    const modes = el("span", "seo-box__modes");
    const bMobile = el("button", "is-active", "Mobile");
    const bDesktop = el("button", "", "Desktop");
    bMobile.type = bDesktop.type = "button";
    modes.append(bMobile, bDesktop);
    label.append(modes);
    const serp = el("div", "serp serp--mobile");
    serp.dir = dir;
    const site = el("div", "serp__site");
    const fav = el("span", "serp__fav", "EG");
    const siteText = el("div");
    const siteName = el("div", "serp__name");
    const url = el("div", "serp__url");
    siteText.append(siteName, url);
    site.append(fav, siteText);
    const serpTitle = el("div", "serp__title");
    const serpDesc = el("div", "serp__desc");
    serp.append(site, serpTitle, serpDesc);
    box.append(label, serp);
    const firstRow = fieldset.querySelector(".form-row");
    firstRow.parentNode.insertBefore(box, firstRow);
    bMobile.addEventListener("click", () => { serp.classList.add("serp--mobile"); bMobile.classList.add("is-active"); bDesktop.classList.remove("is-active"); });
    bDesktop.addEventListener("click", () => { serp.classList.remove("serp--mobile"); bDesktop.classList.add("is-active"); bMobile.classList.remove("is-active"); });

    const titleMeter = titleInput && meter(titleInput, TITLE_MIN, TITLE_MAX);
    const descMeter = descInput && meter(descInput, DESC_MIN, DESC_MAX);
    const hint = el("div", "seo-hint");
    if (titleInput) titleInput.parentNode.append(hint);

    const checks = el("ul", "seo-checks");
    // Inside the <details> of a collapsed fieldset, so it folds away with it.
    (fieldset.querySelector("details") || fieldset).append(checks);
    const heading = fieldset.querySelector("h2, summary");
    const headingDot = el("span", "seo-heading-score");
    if (heading) heading.append(headingDot);

    function render() {
      const title = effectiveTitle(cfg, map, lang);
      const desc = descInput ? descInput.value : "";
      const kw = kwInput.value.trim();
      const origin = cfg.site_url || "";
      const route = (cfg.route || "").replace("{slug}", val("id_slug") || "…");
      siteName.textContent = (cfg.site_titles || {})[lang] || origin.replace(/^https?:\/\//, "");
      url.textContent = [origin, lang, ...route.split("/").filter(Boolean)].join(" › ");
      serpTitle.textContent = truncate(title || "Add an SEO title", TITLE_MAX + 2);
      serpDesc.replaceChildren();
      const shown = truncate(desc || "Add a meta description: Google may otherwise pick any sentence from the page.", DESC_MAX + 2);
      if (kw && has(shown, kw)) {
        // Google bolds the searched phrase in the snippet.
        const i = shown.toLowerCase().indexOf(kw.toLowerCase());
        serpDesc.append(shown.slice(0, i), el("b", "", shown.slice(i, i + kw.length)), shown.slice(i + kw.length));
      } else {
        serpDesc.textContent = shown;
      }
      if (titleMeter) titleMeter(title.length);
      if (descMeter) descMeter(desc.length);
      if (titleInput) {
        titleInput.placeholder = title;
        hint.textContent = titleInput.value ? "" : "Blank: the title above is used automatically.";
      }

      const results = analyse(cfg, map, lang);
      const verdict = score(results);
      checks.replaceChildren(Object.assign(el("li", "seo-checks__title"), {}));
      checks.firstChild.append(dot(verdict), `SEO analysis: ${LABELS[verdict]}`);
      const order = { bad: 0, ok: 1, good: 2 };
      for (const [status, message] of results.sort((a, b) => order[a[0]] - order[b[0]])) {
        const li = el("li", "is-" + status);
        li.append(dot(status), el("span", "", message));
        checks.append(li);
      }
      headingDot.replaceChildren(dot(verdict));
    }

    let frame = 0;
    document.addEventListener("input", () => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(render);
    });
    render();
  }

  document.addEventListener("DOMContentLoaded", () => {
    const node = document.getElementById("seo-box-config");
    if (!node) return;
    const cfg = JSON.parse(node.textContent);
    document.querySelectorAll("fieldset.wp-seo").forEach((fs) => enhance(fs, cfg));
  });
})();
