<template>
  <div
    class="md-prose"
    :class="{ 'md-prose--compact': compact }"
    v-html="html"
  />
</template>

<script setup>
import { computed } from "vue";
import { renderMarkdown } from "../utils/markdownRender.js";

const props = defineProps({
  source: { type: String, default: "" },
  /** Tighter spacing for chat bubbles */
  compact: { type: Boolean, default: false },
});

const html = computed(() => renderMarkdown(props.source));
</script>

<style scoped>
.md-prose {
  font-size: 14px;
  line-height: 1.75;
  color: var(--text-primary);
  word-break: break-word;
}

.md-prose--compact {
  font-size: 13px;
  line-height: 1.7;
}

.md-prose :deep(h1),
.md-prose :deep(h2),
.md-prose :deep(h3),
.md-prose :deep(h4),
.md-prose :deep(h5),
.md-prose :deep(h6) {
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.35;
  margin-top: 1.25em;
  margin-bottom: 0.5em;
}

.md-prose :deep(h1) {
  font-size: 1.5rem;
  padding-bottom: 0.35em;
  border-bottom: 1px solid var(--border-color);
}
.md-prose :deep(h2) {
  font-size: 1.25rem;
}
.md-prose :deep(h3) {
  font-size: 1.1rem;
}
.md-prose :deep(h4) {
  font-size: 1.05rem;
}
.md-prose :deep(h5),
.md-prose :deep(h6) {
  font-size: 1rem;
  color: var(--text-secondary);
}

.md-prose :deep(h1:first-child),
.md-prose :deep(h2:first-child),
.md-prose :deep(h3:first-child) {
  margin-top: 0;
}

.md-prose--compact :deep(h1) {
  font-size: 1.2rem;
}
.md-prose--compact :deep(h2) {
  font-size: 1.1rem;
}
.md-prose--compact :deep(h3) {
  font-size: 1.05rem;
}

.md-prose :deep(p) {
  margin-bottom: 0.85em;
}
.md-prose :deep(p:last-child) {
  margin-bottom: 0;
}

.md-prose :deep(strong) {
  font-weight: 600;
  color: var(--accent-blue);
}

.md-prose :deep(em) {
  font-style: italic;
  color: var(--text-secondary);
}

.md-prose :deep(del) {
  color: var(--text-muted);
}

.md-prose :deep(a) {
  color: var(--accent-blue);
  text-decoration: underline;
  text-underline-offset: 2px;
}
.md-prose :deep(a:hover) {
  color: var(--accent-blue-hover);
}

.md-prose :deep(ul),
.md-prose :deep(ol) {
  margin: 0.65em 0 0.85em;
  padding-left: 1.35em;
}
.md-prose :deep(li) {
  margin: 0.35em 0;
}
.md-prose :deep(li > p) {
  margin-bottom: 0.4em;
}

.md-prose :deep(blockquote) {
  margin: 0.85em 0;
  padding: 0.65em 1em 0.65em 1em;
  border-left: 4px solid var(--accent-blue-border);
  background: var(--accent-blue-light);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  color: var(--text-secondary);
}
.md-prose :deep(blockquote p:last-child) {
  margin-bottom: 0;
}

.md-prose :deep(hr) {
  border: none;
  height: 1px;
  background: var(--border-color);
  margin: 1.25em 0;
}

.md-prose :deep(code) {
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
  font-size: 0.88em;
  padding: 0.15em 0.45em;
  border-radius: 4px;
  background: rgba(37, 99, 235, 0.08);
  color: #1e40af;
}

.md-prose :deep(pre) {
  margin: 0.85em 0;
  padding: 14px 16px;
  border-radius: var(--radius-sm);
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  overflow-x: auto;
  font-size: 0.86em;
  line-height: 1.55;
}
.md-prose :deep(pre code) {
  padding: 0;
  background: none;
  color: var(--text-primary);
  font-size: inherit;
  border-radius: 0;
}

.md-prose :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 0.85em 0;
  font-size: 0.92em;
}
.md-prose :deep(th),
.md-prose :deep(td) {
  border: 1px solid var(--border-color);
  padding: 8px 12px;
  text-align: left;
}
.md-prose :deep(th) {
  background: var(--bg-secondary);
  font-weight: 600;
  color: var(--text-primary);
}
.md-prose :deep(tr:nth-child(even) td) {
  background: var(--bg-secondary);
}

.md-prose :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: var(--radius-sm);
  margin: 0.5em 0;
}
</style>
