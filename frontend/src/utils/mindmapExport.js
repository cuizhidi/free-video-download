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
 * @param {import('markmap-view').Markmap} mm
 * @param {string} [filename]
 * @param {number} [pixelRatio] default: min(3, dpr * 2)
 */
export async function exportMindmapPng(mm, filename = "mindmap.png", pixelRatio) {
  if (!mm) return false;
  const pr =
    pixelRatio ??
    Math.min(3, (typeof window !== "undefined" ? window.devicePixelRatio || 1 : 1) * 2);

  await mm.fit();
  await new Promise((r) => requestAnimationFrame(r));

  const str = buildExportSvgString(mm);
  const svgBlob = new Blob([str], { type: "image/svg+xml;charset=utf-8" });
  const svgUrl = URL.createObjectURL(svgBlob);

  try {
    const img = new Image();
    img.crossOrigin = "anonymous";
    const loaded = new Promise((resolve, reject) => {
      img.onload = () => resolve();
      img.onerror = () => reject(new Error("svg_image_load"));
    });
    img.src = svgUrl;
    await loaded;

    const w = img.naturalWidth || img.width;
    const h = img.naturalHeight || img.height;
    if (!w || !h) {
      URL.revokeObjectURL(svgUrl);
      return false;
    }

    const canvas = document.createElement("canvas");
    canvas.width = Math.ceil(w * pr);
    canvas.height = Math.ceil(h * pr);
    const ctx = canvas.getContext("2d");
    if (!ctx) {
      URL.revokeObjectURL(svgUrl);
      return false;
    }
    ctx.scale(pr, pr);
    ctx.fillStyle = "#fefefe";
    ctx.fillRect(0, 0, w, h);
    ctx.drawImage(img, 0, 0, w, h);

    const pngBlob = await new Promise((resolve) =>
      canvas.toBlob((b) => resolve(b), "image/png")
    );
    URL.revokeObjectURL(svgUrl);
    if (!pngBlob) return false;
    triggerBlobDownload(pngBlob, filename);
    return true;
  } catch {
    URL.revokeObjectURL(svgUrl);
    return false;
  }
}
