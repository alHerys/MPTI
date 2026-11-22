/* Forms: business profile, menu CRUD, daily sales validation, CSV import. */
(function () {
  "use strict";

  function showMessage(node, text, isError) {
    if (!node) { return; }
    node.textContent = text;
    node.className = "form-message " + (isError ? "error" : "success");
  }

  async function api(path, options) {
    var response = await fetch(path, Object.assign({
      headers: { "Content-Type": "application/json", "Accept": "application/json" },
      credentials: "same-origin"
    }, options || {}));
    var body = null;
    try { body = await response.json(); } catch (err) { body = null; }
    if (!response.ok) {
      var detail = body && body.detail;
      if (Array.isArray(detail)) {
        detail = detail.map(function (d) {
          var loc = (d.loc || []).filter(function (part) { return part !== "body"; }).join(".");
          return (loc ? loc + ": " : "") + d.msg;
        }).join("; ");
      }
      throw new Error(detail || ("Gagal menyimpan (kode " + response.status + ")."));
    }
    return body;
  }

  function profileForm() {
    var form = document.getElementById("profile-form");
    if (!form) { return; }
    var message = document.getElementById("profile-message");
    form.addEventListener("submit", async function (event) {
      event.preventDefault();
      var businessId = document.getElementById("profile-panel").getAttribute("data-business-id");
      var data = {
        name: form.name.value.trim(),
        business_type: form.business_type.value,
        location_type: form.location_type.value,
        capacity_factor: parseFloat(form.capacity_factor.value)
      };
      if (!data.name) { showMessage(message, "Nama usaha wajib diisi.", true); return; }
      if (!(data.capacity_factor > 0)) { showMessage(message, "Faktor kapasitas harus lebih dari 0.", true); return; }
      try {
        await api("/api/businesses/" + businessId, { method: "PUT", body: JSON.stringify(data) });
        showMessage(message, "Profil usaha tersimpan.", false);
      } catch (error) {
        showMessage(message, error.message, true);
      }
    });
  }

  function productForm() {
    var form = document.getElementById("product-form");
    if (!form) { return; }
    var toggle = document.getElementById("toggle-product-form");
    var cancel = document.getElementById("cancel-product");
    var message = document.getElementById("product-message");
    var businessId = form.getAttribute("data-business-id");

    function resetForm() {
      form.reset();
      form.product_id.value = "";
      form.salvage_value.value = "0";
      form.classList.add("hidden");
      showMessage(message, "", false);
    }

    if (toggle) {
      toggle.addEventListener("click", function () {
        form.classList.toggle("hidden");
        if (!form.classList.contains("hidden")) { form.name.focus(); }
      });
    }
    if (cancel) { cancel.addEventListener("click", resetForm); }

    form.addEventListener("submit", async function (event) {
      event.preventDefault();
      var price = parseInt(form.price.value, 10);
      var cost = parseInt(form.unit_cost.value, 10);
      var salvage = parseInt(form.salvage_value.value || "0", 10);
      if (!form.name.value.trim()) { showMessage(message, "Nama produk wajib diisi.", true); return; }
      if (!(price > 0)) { showMessage(message, "Harga jual harus lebih besar dari 0.", true); return; }
      if (!(cost >= 0)) { showMessage(message, "Biaya per porsi tidak boleh negatif.", true); return; }
      if (salvage > cost) { showMessage(message, "Nilai sisa tidak boleh melebihi biaya per porsi.", true); return; }
      var payload = {
        name: form.name.value.trim(),
        category: form.category.value,
        price: price,
        unit_cost: cost,
        salvage_value: salvage
      };
      var productId = form.product_id.value;
      try {
        if (productId) {
          await api("/api/products/" + productId, { method: "PUT", body: JSON.stringify(payload) });
        } else {
          await api("/api/businesses/" + businessId + "/products", { method: "POST", body: JSON.stringify(payload) });
        }
        window.location.reload();
      } catch (error) {
        showMessage(message, error.message, true);
      }
    });

    document.querySelectorAll("#product-table .js-edit").forEach(function (button) {
      button.addEventListener("click", function () {
        var row = button.closest("tr");
        var data = JSON.parse(row.getAttribute("data-product"));
        form.product_id.value = data.id;
        form.name.value = data.name;
        form.category.value = data.category;
        form.price.value = data.price;
        form.unit_cost.value = data.unit_cost;
        form.salvage_value.value = data.salvage_value;
        form.classList.remove("hidden");
        form.name.focus();
      });
    });

    document.querySelectorAll("#product-table .js-deactivate").forEach(function (button) {
      button.addEventListener("click", async function () {
        var row = button.closest("tr");
        var data = JSON.parse(row.getAttribute("data-product"));
        if (!window.confirm("Nonaktifkan produk " + data.name + "?")) { return; }
        try {
          await api("/api/products/" + data.id, { method: "DELETE" });
          window.location.reload();
        } catch (error) {
          window.alert(error.message);
        }
      });
    });
  }

  function dailySalesForm() {
    var form = document.getElementById("daily-sales-form");
    if (!form) { return; }
    form.addEventListener("submit", function (event) {
      var invalid = null;
      form.querySelectorAll(".qty-input").forEach(function (input) {
        input.setCustomValidity("");
        var value = input.value.trim();
        if (value === "" || !/^\d+$/.test(value) || parseInt(value, 10) < 0) {
          input.setCustomValidity("Isi jumlah porsi dengan bilangan bulat 0 atau lebih.");
          if (!invalid) { invalid = input; }
        }
      });
      if (invalid) {
        event.preventDefault();
        invalid.reportValidity();
      }
    });
  }

  function importForm() {
    var form = document.getElementById("import-form");
    if (!form) { return; }
    var result = document.getElementById("import-result");
    form.addEventListener("submit", async function (event) {
      event.preventDefault();
      result.innerHTML = "";
      var businessId = form.getAttribute("data-business-id");
      var fileInput = form.querySelector('input[type="file"]');
      if (!fileInput.files.length) {
        result.appendChild(Object.assign(document.createElement("p"), { className: "error", textContent: "Pilih berkas CSV terlebih dahulu." }));
        return;
      }
      var data = new FormData();
      data.append("file", fileInput.files[0]);
      try {
        var response = await fetch("/api/businesses/" + businessId + "/sales/import", {
          method: "POST", body: data, credentials: "same-origin"
        });
        var body = await response.json().catch(function () { return null; });
        if (response.ok) {
          result.appendChild(Object.assign(document.createElement("p"), {
            className: "success", textContent: "Impor berhasil: " + body.accepted + " baris diterima." }));
          return;
        }
        var heading = Object.assign(document.createElement("p"), {
          className: "error", textContent: (body && body.detail) ? body.detail : "Impor gagal (kode " + response.status + ")." });
        result.appendChild(heading);
        var errors = (body && body.errors) || [];
        if (errors.length) {
          var list = document.createElement("ul");
          errors.forEach(function (item) {
            list.appendChild(Object.assign(document.createElement("li"), {
              textContent: "Baris " + item.line + ": " + item.message }));
          });
          result.appendChild(list);
        }
      } catch (error) {
        result.appendChild(Object.assign(document.createElement("p"), {
          className: "error", textContent: "Tidak dapat mengimpor: " + error.message }));
      }
    });
  }

  function init() {
    profileForm();
    productForm();
    dailySalesForm();
    importForm();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
