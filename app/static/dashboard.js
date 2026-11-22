/* Dashboard: fetch recommendations and render cards (T4.4). No hardcoded numbers. */
(function () {
  "use strict";

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) { node.className = className; }
    if (text !== undefined && text !== null) { node.textContent = String(text); }
    return node;
  }

  function formatIdr(value) {
    return "Rp" + Number(value).toLocaleString("id-ID");
  }

  function confidenceLabel(level) {
    if (level === "tinggi") { return "Tinggi"; }
    if (level === "sedang") { return "Sedang"; }
    return "Rendah";
  }

  function markerPosition(p10, p90, qty) {
    var span = Math.max(p90 - p10, 1);
    var ratio = (qty - p10) / span;
    var clamped = Math.min(Math.max(ratio, 0), 1);
    return (clamped * 100).toFixed(1) + "%";
  }

  function renderCard(item) {
    var card = el("article", "rec-card");
    card.setAttribute("data-product-id", item.product_id);

    card.appendChild(el("h3", null, item.name));
    card.appendChild(el("div", "rec-qty", "Produksi ± " + item.recommended_qty + " porsi"));

    var range = el("div", "rec-range");
    var track = el("div", "range-track");
    var marker = el("div", "range-marker");
    marker.style.left = markerPosition(item.p10, item.p90, item.recommended_qty);
    marker.title = "Rekomendasi " + item.recommended_qty + " porsi";
    track.appendChild(marker);
    range.appendChild(track);
    var labels = el("div", "range-labels");
    labels.appendChild(el("span", null, "P10 " + item.p10));
    labels.appendChild(el("span", null, "P50 " + item.p50));
    labels.appendChild(el("span", null, "P90 " + item.p90));
    range.appendChild(labels);
    card.appendChild(range);

    var meta = el("div", "rec-meta");
    meta.appendChild(el("span", "badge badge-" + item.confidence, confidenceLabel(item.confidence)));
    meta.appendChild(el("span", "badge badge-stage", item.stage));
    meta.appendChild(el("span", "badge badge-stage", item.n_days + " hari data"));
    meta.appendChild(el("span", "badge badge-stage", "Target " + Math.round(item.alpha * 100) + "%"));
    card.appendChild(meta);

    var alpha = el("p", "muted", "Peluang cukup stok " + Math.round(item.alpha * 100) + "% · band terdekat " + item.nearest_band);
    card.appendChild(alpha);

    var details = el("details", "reasons");
    details.appendChild(el("summary", null, "Mengapa rekomendasi ini?"));
    var list = el("ul");
    (item.reasons || []).forEach(function (reason) { list.appendChild(el("li", null, reason)); });
    details.appendChild(list);
    card.appendChild(details);
    return card;
  }

  function renderError(grid, note, message) {
    grid.innerHTML = "";
    note.textContent = "Gagal memuat rekomendasi.";
    var box = el("p", "error", message);
    grid.appendChild(box);
  }

  function init() {
    var note = document.getElementById("stage-note");
    var grid = document.getElementById("recommendation-grid");
    if (!note || !grid) { return; }
    var businessId = note.getAttribute("data-business-id");
    var targetDate = note.getAttribute("data-date");
    var url = "/api/businesses/" + encodeURIComponent(businessId) +
      "/recommendations?date=" + encodeURIComponent(targetDate);

    fetch(url, { headers: { "Accept": "application/json" }, credentials: "same-origin" })
      .then(function (response) {
        if (response.status === 401) { window.location.href = "/login"; throw new Error("Sesi berakhir."); }
        if (!response.ok) { throw new Error("Respons " + response.status); }
        return response.json();
      })
      .then(function (payload) {
        grid.innerHTML = "";
        var items = payload.items || [];
        var stages = {};
        items.forEach(function (item) {
          stages[item.stage] = true;
          grid.appendChild(renderCard(item));
        });
        var stageKeys = Object.keys(stages).sort();
        note.textContent = items.length
          ? "Tahap data: " + stageKeys.join(" / ") + " · " + items.length + " produk aktif · tanggal " + payload.date
          : "Belum ada produk aktif untuk usaha ini.";
      })
      .catch(function (error) {
        renderError(grid, note, "Tidak dapat memuat rekomendasi: " + error.message);
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
