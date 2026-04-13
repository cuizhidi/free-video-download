import { toBlob } from "html-to-image";

const PAD = 28;

function buildExportSvgString(mm) {
  const g = mm.g.node();
  const bbox = g.getBBox();
  const orig = mm.svg.node();
  const clone = orig.cloneNode(true);
  const styleEl = document.createElementNS("http://www.w3.org/2000/svg", "style");
  styleEl.textContent = mm.getStyleContent();
  clone.insertBefore(styleEl, clone.firstChild);
  clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
  const vbX = bbox.x - PAD;
  const vbY = bbox.y - PAD;
  const vbW = bbox.width + PAD * 2;
  const vbH = bbox.height + PAD * 2;
  clone.setAttribute("viewBox", `${vbX} ${vbY} ${vbW} ${vbH}`);
  clone.setAttribute("width", String(Math.ceil(vbW)));
  clone.setAttribute("height", String(Math.ceil(vbH)));
  const serializer = new XMLSerializer();
  return serializer.serializeToString(clone);
}

export function triggerBlobDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.rel = "noopener";
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2500);
}

/**
 * @param {import('markmap-view').Markmap} mm
 * @param {string} [filename]
 */
export async function exportMindmapSvg(mm, filename = "mindmap.svg") {
  if (!mm) return false;
  await mm.fit();
  await new Promise((r) => requestAnimationFrame(r));
  const str = buildExportSvgString(mm);
  const blob = new Blob([str], { type: "image/svg+xml;charset=utf-8" });
  triggerBlobDownload(blob, filename);
  return true;
}

/**
 * Export mindmap as PNG using html-to-image which correctly handles
 * SVG foreignObject elements (markmap renders text via foreignObject).
 *
 * @param {import('markmap-view').Markmap} mm
 * @param {string} [filename]
 * @param {number} [pixelRatio]
 */
export async function exportMindmapPng(mm, filename = "mindmap.png", pixelRatio) {
  if (!mm) return false;
  const pr =
    pixelRatio ??
    Math.min(3, (typeof window !== "undefined" ? window.devicePixelRatio || 1 : 1) * 2);

  await mm.fit();
  await new Promise((r) => requestAnimationFrame(r));

  const svgNode = mm.svg.node();
  if (!svgNode) return false;

  try {
    const blob = await toBlob(svgNode, {
      pixelRatio: pr,
      backgroundColor: "#fefefe",
      filter: (node) => {
        if (node instanceof HTMLElement && node.tagName === "NOSCRIPT") return false;
        return true;
      },
    });
    if (!blob) return false;
    triggerBlobDownload(blob, filename);
    return true;
  } catch (e) {
    console.warn("[mindmapExport] PNG export failed:", e);
    return false;
  }
}
