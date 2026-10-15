async function request(path, options = {}) {
  const response = await fetch(path, options);
  const data = await response.json().catch(function () { return { error: response.statusText }; });
  if (!response.ok) throw new Error(typeof data === "string" ? data : JSON.stringify(data, null, 2));
  return data;
}

function $(id) { return document.getElementById(id); }
function pretty(target, data) { target.textContent = JSON.stringify(data, null, 2); }

async function loadDashboard() {
  const results = await Promise.all([request("/api/health"), request("/api/dashboard")]);
  const health = results[0];
  const dashboard = results[1];
  $("status-text").textContent = health.ok ? ("Online · " + health.version) : "Unavailable";
  $("status-dot").classList.toggle("ok", Boolean(health.ok));
  $("m-cases").textContent = dashboard.Total_Cases || 0;
  $("m-evidence").textContent = dashboard.Total_Evidence_Objects || 0;
  $("m-claims").textContent = dashboard.Total_Claims || 0;
  $("m-experiments").textContent = dashboard.Total_Experiments || 0;
  $("m-events").textContent = dashboard.Provenance_Events || 0;
  $("m-failed").textContent = dashboard.Failed_Audits || 0;
}

$("claim-form").addEventListener("submit", async function (event) {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(event.currentTarget).entries());
  try {
    pretty($("claim-output"), await request("/api/claims/validate", {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload)
    }));
  } catch (error) { $("claim-output").textContent = "Error: " + error.message; }
});

async function inventory(kind) {
  const form = new FormData($("inventory-form"));
  const payload = { path: form.get("path"), recursive: form.get("recursive") === "on" };
  const endpoint = kind === "cbom" ? "/api/inventory/cbom" : "/api/inventory/scan";
  try {
    pretty($("inventory-output"), await request(endpoint, {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload)
    }));
  } catch (error) { $("inventory-output").textContent = "Error: " + error.message; }
}

$("inventory-form").addEventListener("submit", function (event) {
  event.preventDefault();
  inventory("scan");
});
$("cbom").addEventListener("click", function () { inventory("cbom"); });

$("audit").addEventListener("click", async function () {
  try { pretty($("audit-output"), await request("/api/provenance/audit")); }
  catch (error) { $("audit-output").textContent = "Error: " + error.message; }
});

$("refresh").addEventListener("click", function () {
  loadDashboard().catch(function (error) {
    $("status-text").textContent = "Service check failed";
    $("status-dot").classList.remove("ok");
    console.error(error);
  });
});

loadDashboard().catch(function (error) {
  $("status-text").textContent = "Service check failed";
  console.error(error);
});
