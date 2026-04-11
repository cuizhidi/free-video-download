import { marked } from "marked";
import DOMPurify from "dompurify";

marked.setOptions({
  gfm: true,
  breaks: true,
});

/**
 * Render markdown to safe HTML for v-html.
 * @param {string} source
 * @returns {string}
 */
export function renderMarkdown(source) {
  if (!source || typeof source !== "string") return "";
  const raw = marked.parse(source, { async: false });
  return DOMPurify.sanitize(raw, {
    USE_PROFILES: { html: true },
  });
}
