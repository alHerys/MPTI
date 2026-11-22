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
    var template = document.getElementById("rec-card-template");
    var card = template.content.firstElementChild.cloneNode(true);
    var field = function (name) { return card.querySelector('[data-field="' + name + '"]'); };

    card.setAttribute("data-product-id", item.product_id);
    field("name").textContent = item.name;
    field("qty").textContent = "Produksi ± " + item.recommended_qty + " porsi";

    var marker = field("marker");
    marker.style.left = markerPosition(item.p10, item.p90, item.recommended_qty);
    marker.title = "Rekomendasi " + item.recommended_qty + " porsi";

    field("p10").textContent = "P10 " + item.p10;
    field("p50").textContent = "P50 " + item.p50;
    field("p90").textContent = "P90 " + item.p90;

    var confidence = field("confidence");
    confidence.classList.add("badge-" + item.confidence);
    confidence.textContent = confidenceLabel(item.confidence);
    field("stage").textContent = item.stage;
    field("days").textContent = item.n_days + " hari data";
    field("target").textContent = "Target " + Math.round(item.alpha * 100) + "%";
    field("band").textContent = "Peluang cukup stok " + Math.round(item.alpha * 100) +
      "% · band terdekat " + item.nearest_band;

    var list = field("reasons");
    (item.reasons || []).forEach(function (reason) {
      list.appendChild(el("li", null, reason));
    });
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
