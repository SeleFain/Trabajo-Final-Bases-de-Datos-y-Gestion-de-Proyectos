let reportCatalog = [];
let activeReport = null;
let reportRequest = 0;
const $ = (selector) => document.querySelector(selector);
const money = new Intl.NumberFormat("es-AR", { style: "currency", currency: "USD", maximumFractionDigits: 2 });
const integer = new Intl.NumberFormat("es-AR");
const labels = {
  id_cliente: "ID cliente", nombre_cliente: "Cliente", segmento: "Segmento",
  id_categoria: "ID categoría", categoria: "Categoría", id_subcategoria: "ID subcategoría",
  subcategoria: "Subcategoría", id_producto: "ID producto", codigo_producto: "Código",
  nombre_producto: "Producto", id_envio: "ID envío", modo_envio: "Modo de envío",
  id_pedido: "ID pedido", fecha_pedido: "Fecha del pedido", fecha_envio: "Fecha de envío",
  pais: "País", ciudad: "Ciudad", estado: "Estado", codigo_postal: "Código postal",
  region: "Región", id_fila: "ID fila", ventas: "Ventas", cantidad: "Cantidad",
  descuento: "Descuento", ganancia: "Ganancia", lineas_vendidas: "Líneas vendidas",
  unidades_vendidas: "Unidades vendidas", ventas_totales: "Ventas totales",
  ganancia_total: "Ganancia total", cantidad_pedidos: "Cantidad de pedidos",
  total_clientes: "Clientes", total_pedidos: "Pedidos", total_productos: "Productos",
  unidades_vendidas: "Unidades vendidas"
};
function humanize(value) { return labels[value] || value.replaceAll("_", " ").replace(/^./, c => c.toUpperCase()); }
function showToast(message) { const el = $("#toast"); el.textContent = message; el.classList.add("show"); setTimeout(() => el.classList.remove("show"), 4000); }
async function api(url) {
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || "No se pudo completar la consulta.");
  return data;
}
function formatValue(key, value) {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "number") {
    if (/ventas|ganancia|profit|sales/i.test(key)) return money.format(value);
    if (/descuento/i.test(key)) return `${(value * 100).toLocaleString("es-AR", {maximumFractionDigits: 2})}%`;
    if (Number.isInteger(value)) return integer.format(value);
    return value.toLocaleString("es-AR", {maximumFractionDigits: 2});
  }
  return String(value);
}
function renderTable(head, body, columns, rows) {
  head.replaceChildren(); body.replaceChildren();
  const headerRow = document.createElement("tr");
  columns.forEach(column => { const th = document.createElement("th"); th.textContent = humanize(column); headerRow.appendChild(th); });
  head.appendChild(headerRow);
  if (!rows.length) {
    const tr = document.createElement("tr"); const td = document.createElement("td");
    td.colSpan = Math.max(columns.length, 1); td.className = "empty"; td.textContent = "La consulta no devolvió registros.";
    tr.appendChild(td); body.appendChild(tr); return;
  }
  rows.forEach(row => {
    const tr = document.createElement("tr");
    columns.forEach(column => { const td = document.createElement("td"); td.textContent = formatValue(column, row[column]); tr.appendChild(td); });
    body.appendChild(tr);
  });
}
function setView(view) {
  document.querySelectorAll(".view").forEach(el => el.classList.toggle("active", el.id === `view-${view}`));
  document.querySelectorAll(".nav-item").forEach(el => el.classList.toggle("active", el.dataset.view === view));
  $("#page-title").textContent = ({dashboard: "Resumen general", tablas: "Explorar tablas", reportes: "Reportes SQL"})[view];
}
document.querySelectorAll("[data-view]").forEach(button => button.addEventListener("click", () => setView(button.dataset.view)));
async function loadStatus() {
  try { await api("/api/estado"); $("#connection-text").textContent = "Base de datos conectada"; $("#status-dot").classList.add("connected"); }
  catch { $("#connection-text").textContent = "Sin conexión a la base"; $("#status-dot").classList.add("disconnected"); }
}
async function loadDashboard() {
  try {
    const data = await api("/api/indicadores");
    $("#kpi-sales").textContent = money.format(Number(data.ventas_totales || 0));
    $("#kpi-profit").textContent = money.format(Number(data.ganancia_total || 0));
    $("#kpi-orders").textContent = integer.format(Number(data.total_pedidos || 0));
    $("#kpi-customers").textContent = integer.format(Number(data.total_clientes || 0));
  } catch (error) { showToast(error.message); }
}
async function loadTables() {
  try {
    const tables = await api("/api/tablas");
    const select = $("#table-select"); select.replaceChildren();
    tables.forEach(table => { const option = document.createElement("option"); option.value = table.nombre; option.textContent = table.etiqueta; select.appendChild(option); });
    if (tables.length) await loadTable(select.value);
  } catch (error) { showToast(error.message); }
}
async function loadTable(name) {
  if (!name) return;
  try {
    const data = await api(`/api/tablas/${encodeURIComponent(name)}`);
    renderTable($("#data-head"), $("#data-body"), data.columnas, data.filas);
    $("#table-count").textContent = `${integer.format(data.total)} registros`;
    $("#table-footer").textContent = `Mostrando ${integer.format(data.filas.length)} de ${integer.format(data.total)} registros · Consulta de solo lectura`;
  } catch (error) { showToast(error.message); }
}
$("#table-select").addEventListener("change", event => loadTable(event.target.value));
async function loadReports() {
  try {
    const reports = await api("/api/reportes"); reportCatalog = reports; const list = $("#report-list"); list.replaceChildren();
    reports.forEach((report, index) => {
      const button = document.createElement("button"); button.className = "report-option"; button.dataset.report = report.id;
      button.innerHTML = `<span class="report-number">${String(index + 1).padStart(2, "0")}</span><span><strong></strong><small></small></span><span>→</span>`;
      button.querySelector("strong").textContent = report.titulo; button.querySelector("small").textContent = report.descripcion;
      button.addEventListener("click", () => runReport(report.id)); list.appendChild(button);
    });
    if (reports.length) await runReport(reports[0].id);
  } catch (error) { showToast(error.message); }
}
async function runReport(id) {
  if (activeReport !== id) {
    activeReport = id;
    $("#report-filters").reset();
    $("#filter-limit").value = ["top_clientes", "productos_vendidos"].includes(id) ? 10 : 100;
    const fields = reportCatalog.find(r => r.id === id)?.campos || [];
    $("#filter-field").replaceChildren(...fields.map(field => {
      const option = document.createElement("option"); option.value = field; option.textContent = humanize(field); return option;
    }));
  }
  const currentRequest = ++reportRequest;
  $("#report-status").textContent = "Consultando…";
  $("#report-body").replaceChildren(); $("#report-head").replaceChildren();
  $("#report-sql").textContent = "Consultando…"; $("#report-params").textContent = "";
  try {
    const params = new URLSearchParams(new FormData($("#report-filters")));
    const report = await api(`/api/reportes/${encodeURIComponent(id)}?${params}`);
    if (currentRequest !== reportRequest) return;
    $("#report-sql").textContent = report.sql;
    $("#report-params").textContent = JSON.stringify(report.parametros, null, 2);
    $("#report-status").textContent = `${report.filas.length} resultados · Filtros aplicados en SQL`;
    $("#report-title").textContent = report.titulo; $("#report-description").textContent = report.descripcion;
    renderTable($("#report-head"), $("#report-body"), report.columnas, report.filas);
    document.querySelectorAll(".report-option").forEach(el => el.classList.toggle("selected", el.dataset.report === id));
    setView("reportes");
  } catch (error) {
    if (currentRequest !== reportRequest) return;
    $("#report-status").textContent = error.message;
    $("#report-sql").textContent = "Consulta no disponible.";
    showToast(error.message);
  }
}
$("#report-filters").addEventListener("submit", event => {
  event.preventDefault(); if (activeReport) runReport(activeReport);
});
$("#clear-filters").addEventListener("click", () => {
  if (!activeReport) return;
  const id = activeReport; activeReport = null; runReport(id);
});
document.querySelectorAll("[data-report]").forEach(button => button.addEventListener("click", () => runReport(button.dataset.report)));
$("#refresh-dashboard").addEventListener("click", loadDashboard);
(async function init() { await loadStatus(); await Promise.all([loadDashboard(), loadTables(), loadReports()]); })();
