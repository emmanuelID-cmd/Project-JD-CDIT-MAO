const $ = (s, root=document) => root.querySelector(s);
let displayedWarning = "";
const esc = value => String(value ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
const pretty = value => String(value || "unknown").replaceAll("_"," ").replace(/\b\w/g, c => c.toUpperCase());
async function api(url, options={}) {
  const response = await fetch(url, {...options, credentials:"same-origin", headers:{"Content-Type":"application/json", ...(options.headers || {})}});
  if (response.status === 401) { location.assign("/login?next=" + encodeURIComponent(location.pathname)); throw new Error("Your session ended. Sign in again."); }
  const text = await response.text();
  let data = {};
  try { data = text ? JSON.parse(text) : {}; } catch { data = {}; }
  if (!response.ok) throw new Error(data.detail || "The request could not be completed.");
  return data;
}
function showMessage(node, message, kind="") { if (!node) return; node.textContent=message; node.className="form-message " + kind; }
function statusPill(status) { return '<span class="status-pill ' + (status === "unknown" ? "unknown" : "") + '">' + esc(pretty(status)) + '</span>'; }
function statusOptions(current, allowed) {
  return (allowed || []).map(value => '<option value="' + esc(value) + '"' + (value === current ? ' selected' : '') + '>' + esc(pretty(value)) + '</option>').join("");
}
function cardForCase(item, role) {
  const displayStatus = item.display_status || item.status;
  const kind = item.record_kind === "development_example" ? '<span class="role-pill">Development example</span>' : '<span class="role-pill">Client request</span>';
  const rationale = item.catalog_rationale ? '<p class="helper">Example context: ' + esc(item.catalog_rationale) + '</p>' : '';
  let controls = '';
  if (role === "user" && item.can_edit) {
    controls = '<form class="case-edit-form" data-case-edit="' + esc(item.case_id) + '"><label>Request title<input name="subject" maxlength="160" value="' + esc(item.subject) + '" required></label><label>Request details<textarea name="request_text" maxlength="12000" rows="3" required>' + esc(item.request_text) + '</textarea></label><button class="button secondary" type="submit">Save changes</button><span class="form-message" role="status"></span></form>';
  } else if (role === "user" && item.can_cancel) {
    controls = '<span class="helper">Editing is locked while support reviews this request.</span><button class="button secondary danger" type="button" data-case-cancel="' + esc(item.case_id) + '">Cancel as unresolved</button>';
  } else if (role !== "user") {
    controls = '<form class="case-edit-form" data-case-edit="' + esc(item.case_id) + '"><label>Request title<input name="subject" maxlength="160" value="' + esc(item.subject) + '" required></label><label>Request details<textarea name="request_text" maxlength="12000" rows="3" required>' + esc(item.request_text) + '</textarea></label><div class="row-actions"><button class="button secondary" type="submit">Save case details</button>' + (item.allowed_next_statuses.length ? '<label class="status-control">Change status<select name="next_status" required><option value="">Choose status</option>' + statusOptions("", item.allowed_next_statuses) + '</select></label><button class="button primary" type="button" data-case-status="' + esc(item.case_id) + '">Update status</button>' : '<span class="helper">Closed is terminal.</span>') + '</div><span class="form-message" role="status"></span></form>';
  } else {
    controls = '<span class="helper">' + (item.closure_reason === "requester_cancelled_unresolved" ? "Cancelled by you as unresolved." : "This request is no longer editable.") + '</span>';
  }
  return '<article class="case-card"><div><div class="case-meta">' + kind + (role !== "user" ? '<span class="case-id">Owner ' + esc(item.owner_account_id) + '</span>' : '') + '</div><h3>' + esc(item.subject) + '</h3><p>' + esc(item.request_text) + '</p>' + rationale + '<div class="case-meta"><span class="case-id">' + esc(item.case_id) + '</span>' + statusPill(displayStatus) + statusPill(item.urgency_band) + '<span>Created ' + esc(new Date(item.created_at).toLocaleString()) + '</span></div></div><div class="case-actions">' + controls + '</div></article>';
}
function empty(message) { return '<div class="empty-state"><b>' + esc(message) + '</b><span>There are no synthetic records to show.</span></div>'; }
function setNav(role) {
  const items = role === "user"
    ? [["/app/user","▤","My requests"],["#new-request","＋","New request"]]
    : role === "staff"
    ? [["/app/staff","▤","Work queue"],["#product-health","⌁","Product Health"]]
    : [["/app/admin","▤","Overview"],["#accounts","♙","Accounts & access"],["#product-health","⌁","Product Health"],["#extension-alerts","◷","Session requests"]];
  $("#workspace-label").textContent = role === "user" ? "CLIENT WORKSPACE" : role === "staff" ? "SUPPORT OPERATIONS" : "ADMINISTRATION";
  $("#side-nav").innerHTML = items.map((item,i)=>'<a class="nav-item ' + (i===0 ? "active" : "") + '" href="' + item[0] + '"><span>' + item[1] + '</span>' + item[2] + '</a>').join("");
  $("#actor-role").textContent = role === "user" ? "Client view" : role === "staff" ? "Support operations" : "Privileged access";
  $("#avatar").className = "avatar " + role;
  $("#avatar").textContent = role[0].toUpperCase();
  const title = role === "user" ? "Your support desk" : role === "staff" ? "Work queue" : "Access & system health";
  const crumb = role === "user" ? "CLIENT WORKSPACE / REQUESTS" : role === "staff" ? "SUPPORT OPERATIONS / WORKBENCH" : "ADMINISTRATION / OVERVIEW";
  const description = role === "user" ? "Send a request and follow its current status. A human support specialist reviews every case." : role === "staff" ? "Review synthetic requests, system evidence, and human-review handoffs." : "Manage synthetic accounts and inspect operational metadata. All changes are locally audited.";
  $("#page-title").textContent=title; $("#crumb").textContent=crumb; $("#page-description").textContent=description;
  $("#today").textContent=new Date().toLocaleDateString(undefined,{weekday:"short",month:"short",day:"numeric",year:"numeric"});
}
function renderMetrics(role, cases, accounts=[], alerts=[]) {
  const open = cases.filter(c=>["submitted","in_progress","waiting_on_customer","escalated"].includes(c.status)).length;
  const values = role === "user"
    ? [["YOUR REQUESTS",cases.length,"Visible to your account"],["IN REVIEW",open,"Status shown for your requests"],["HUMAN REVIEW","On","Agents cannot resolve or change tickets"]]
    : role === "staff"
    ? [["CASES IN VIEW",cases.length,"Synthetic records only"],["NEEDS REVIEW",open,"Submitted or awaiting review"],["AGENT AUTHORITY","Draft","Human case controls; agents remain read-only"]]
    : [["SYNTHETIC ACCOUNTS",accounts.length,"User, Staff, Admin"],["ACTIVE CASES",cases.length,"Human-reviewed support queue"],["OPEN SESSION REQUESTS",alerts.filter(a=>a.review_status==="new").length,"Review only; no time extension"]];
  $("#metrics").innerHTML=values.map((x,i)=>'<article class="metric-card ' + (i===2 ? "accent" : "") + '"><span>' + esc(x[0]) + '</span><b>' + esc(x[1]) + '</b><small>' + esc(x[2]) + '</small></article>').join("");
}
function renderCases(cases, role) {
  const root=$("#case-list");
  root.innerHTML=cases.length ? cases.map(c=>cardForCase(c,role)).join("") : empty(role==="user" ? "No requests yet" : "Queue is clear");
}
function requestForm() {
  return '<section class="panel" id="new-request"><div class="panel-heading"><div><div class="eyebrow">CREATE A CASE</div><h2>Tell us what you need</h2><p class="muted">Synthetic prototype only. Do not enter real personal, health, or customer information.</p></div><span class="panel-icon">＋</span></div><form id="request-form" class="stack-form"><label for="subject">Request title</label><input id="subject" name="subject" maxlength="160" placeholder="e.g. Report export access" required><label for="request-text">What happened or what do you need?</label><textarea id="request-text" name="request_text" maxlength="12000" rows="5" placeholder="Describe your synthetic support request." required></textarea><div class="form-bottom"><span class="helper">Synthetic examples only · 12,000 character maximum</span><button class="button primary" type="submit">Submit request <span aria-hidden="true">→</span></button></div><div id="request-message" class="form-message" role="status" aria-live="polite"></div></form></section>';
}
function renderStaffPanels(role) {
  const header = '<div class="section-head"><div><h2>' + (role==="user" ? "Recent requests" : "Case queue") + '</h2><p class="muted">' + (role==="user" ? "Only requests submitted by this account appear here." : "Manage the synthetic queue and the 80 tagged development examples. Agent outputs remain proposals.") + '</p></div>' + (role==="user" ? '<button class="button secondary" data-scroll="#new-request">＋ New request</button>' : '<button class="button secondary" id="refresh-cases">↻ Refresh</button>') + '</div><div id="case-list" class="case-list" aria-live="polite"><div class="loading-card"><span class="spinner"></span> Loading synthetic cases…</div></div>';
  let body=header;
  if(role==="user") body+=requestForm();
  if(role!=="user") body+='<section class="panel" id="product-health"><div class="panel-heading"><div><div class="eyebrow">SYSTEM SIGNALS</div><h2>Product Health</h2><p class="muted">Allowlisted synthetic metadata only. Ticket bodies and arbitrary model text are not stored here.</p></div><span class="panel-icon blue">⌁</span></div><div id="health-events" class="health-list"><div class="loading-card"><span class="spinner"></span> Loading metadata…</div></div></section>';
  if(role==="admin") body+='<section class="panel" id="accounts"><div class="panel-heading"><div><div class="eyebrow">PRIVILEGED CONTROLS</div><h2>Accounts & access</h2><p class="muted">Change role or status for synthetic accounts. Changes record before/after values.</p></div><span class="panel-icon violet">♙</span></div><div id="account-list" class="table-wrap"><div class="loading-card"><span class="spinner"></span> Loading accounts…</div></div></section><section class="panel" id="extension-alerts"><div class="panel-heading"><div><div class="eyebrow">SESSION OVERSIGHT</div><h2>Session review requests</h2><p class="muted">Reviewing never extends a session.</p></div><span class="panel-icon">◷</span></div><div id="extension-list" class="health-list"><div class="loading-card"><span class="spinner"></span> Loading requests…</div></div></section>';
  $("#view-content").innerHTML=body;
}
function renderHealth(data) {
  const root=$("#health-events"); if(!root)return;
  const events=data.events||[];
  root.innerHTML=events.length ? events.map(e=>'<div class="health-row"><div><b>' + esc(pretty(e.event_type)) + '</b><small>' + esc(e.component) + ' · v' + esc(e.component_version) + ' · ' + esc(new Date(e.occurred_at).toLocaleString()) + '</small></div><span class="health-code">' + esc(e.error_code || e.status_code || "recorded") + '</span></div>').join("") : empty("No Product Health events");
}
function renderAccounts(accounts) {
  const root=$("#account-list"); if(!root)return;
  root.innerHTML='<table class="data-table"><thead><tr><th>Account</th><th>Role</th><th>Status</th><th>Change role</th><th>Access</th></tr></thead><tbody>' + accounts.map(a=>'<tr><td><b>' + esc(a.username) + '</b><div class="case-id">' + esc(a.account_id) + '</div></td><td><span class="role-pill">' + esc(pretty(a.role)) + '</span></td><td>' + esc(pretty(a.status)) + '</td><td><div class="row-actions"><select class="select-field" aria-label="New role for ' + esc(a.username) + '" data-role-select="' + esc(a.account_id) + '"><option value="">No change</option><option value="user">User</option><option value="staff">Staff</option><option value="admin">Admin</option></select><button class="button secondary" data-role-save="' + esc(a.account_id) + '">Save</button></div></td><td><div class="row-actions"><select class="select-field" aria-label="New status for ' + esc(a.username) + '" data-status-select="' + esc(a.account_id) + '"><option value="">No change</option><option value="active">Active</option><option value="suspended">Suspend</option><option value="deactivated">Deactivate</option><option value="removed">Remove</option></select><button class="button secondary" data-status-save="' + esc(a.account_id) + '">Save</button></div></td></tr>').join("") + '</tbody></table><div id="admin-message" class="form-message" role="status" aria-live="polite"></div>';
}
function renderAlerts(alerts) {
  const root=$("#extension-list"); if(!root)return;
  root.innerHTML=alerts.length ? alerts.map(a=>'<div class="health-row"><div><b>' + esc(a.username) + '</b><small>' + esc(a.alert_id) + ' · requested ' + esc(new Date(a.requested_at).toLocaleString()) + '</small></div>' + (a.review_status==="new" ? '<button class="button secondary" data-alert-review="' + esc(a.alert_id) + '">Mark reviewed</button>' : '<span class="status-pill">Reviewed</span>') + '</div>').join("") : empty("No session review requests");
}
async function loadData(role) {
  const cases=await api("/api/cases");
  renderCases(cases,role);
  let accounts=[],alerts=[];
  if(role==="admin"){ [accounts,alerts]=await Promise.all([api("/api/admin/accounts"),api("/api/admin/session-extension-alerts")]); renderAccounts(accounts); renderAlerts(alerts); }
  if(role!=="user") renderHealth(await api("/api/product-health"));
  renderMetrics(role,cases,accounts,alerts);
}
async function loadSession() {
  try {
    const state=await api("/auth/session");
    if(!state.authenticated){location.assign("/login");return;}
    const modal=$("#session-modal"); if(!modal)return;
    if(state.warning){
      const warningKey=state.warning + "|" + state.expires_at;
      if(warningKey !== displayedWarning){
        const level=state.warning==="5m" ? "about five minutes" : "about fifteen minutes";
        $("#session-copy").textContent="Your session reaches its current limit in " + level + ". You can save your work and sign out, stay signed in to reset the inactivity timer, or send an extension request for Admin review. The 8-hour maximum still applies.";
        modal.hidden=false; displayedWarning=warningKey; $("#session-continue").focus();
      }
    } else { displayedWarning=""; }
  } catch(error) { console.warn(error); }
}
async function start() {
  const role= document.body.dataset.role;
  if(!role)return;
  try {
    const actor=await api("/auth/me");
    if(actor.role!==role){location.replace("/app/"+actor.role);return;}
    $("#actor-name").textContent=actor.username; setNav(role); renderStaffPanels(role);
    await loadData(role);
    if(role==="user") $("#request-form").addEventListener("submit",submitRequest);
    const refresh=$("#refresh-cases"); if(refresh)refresh.addEventListener("click",()=>loadData(role).catch(e=>showMessage($("#admin-message"),e.message,"error")));
    document.addEventListener("click", async e=>{
      const scroll=e.target.closest("[data-scroll]"); if(scroll){e.preventDefault();document.querySelector(scroll.dataset.scroll)?.scrollIntoView({behavior:"smooth"});}
      const roleSave=e.target.closest("[data-role-save]"); if(roleSave){const id=roleSave.dataset.roleSave;const select=document.querySelector('[data-role-select="' + id + '"]');if(select.value)await adminChange(id,{role:select.value},role);else showMessage($("#admin-message"),"Choose a role first.");}
      const statusSave=e.target.closest("[data-status-save]"); if(statusSave){const id=statusSave.dataset.statusSave;const select=document.querySelector('[data-status-select="' + id + '"]');if(select.value)await adminChange(id,{status:select.value},role);else showMessage($("#admin-message"),"Choose an access status first.");}
      const review=e.target.closest("[data-alert-review]"); if(review)try{await api("/api/admin/session-extension-alerts/"+encodeURIComponent(review.dataset.alertReview)+"/review",{method:"PATCH"});await loadData(role);}catch(err){showMessage($("#admin-message"),err.message,"error");}
    });
    document.addEventListener("click", async e=>{
      const cancel=e.target.closest("[data-case-cancel]");
      if(cancel){
        if(!window.confirm("Cancel this request as unresolved? This closes your request and cannot be undone."))return;
        try{await api("/api/cases/"+encodeURIComponent(cancel.dataset.caseCancel)+"/cancel",{method:"POST"});await loadData(role);}catch(error){showMessage(cancel.closest(".case-card").querySelector(".form-message"),error.message,"error");}
      }
      const update=e.target.closest("[data-case-status]");
      if(update){
        const form=update.closest("form");const status=form.elements.next_status.value;
        if(!status){showMessage(form.querySelector(".form-message"),"Choose a status first.","error");return;}
        try{await api("/api/cases/"+encodeURIComponent(update.dataset.caseStatus)+"/status",{method:"PATCH",body:JSON.stringify({status})});await loadData(role);}catch(error){showMessage(form.querySelector(".form-message"),error.message,"error");}
      }
    });
    document.addEventListener("submit", async e=>{
      const form=e.target.closest("form[data-case-edit]");if(!form)return;
      e.preventDefault();const caseId=form.dataset.caseEdit;const message=form.querySelector(".form-message");
      try{await api("/api/cases/"+encodeURIComponent(caseId),{method:"PATCH",body:JSON.stringify({subject:form.elements.subject.value,request_text:form.elements.request_text.value})});await loadData(role);}
      catch(error){showMessage(message,error.message,"error");}
    });    $("#logout").addEventListener("click",signOut);
    $("#session-logout").addEventListener("click",signOut);
    $("#session-continue").addEventListener("click",async()=>{try{await api("/auth/continue",{method:"POST"});$("#session-modal").hidden=true;}catch(e){showMessage($("#session-message"),e.message,"error");}});
    $("#session-extend-request").addEventListener("click",async()=>{try{await api("/auth/extension-request",{method:"POST"});showMessage($("#session-message"),"Request recorded for Admin review. Your session was not extended.","success");}catch(e){showMessage($("#session-message"),e.message,"error");}});
    await loadSession(); setInterval(loadSession,30000);
  } catch(error) {
    console.error(error);
    $("#crumb").textContent="RECOVERY"; $("#page-title").textContent="Workspace unavailable";
    $("#page-description").textContent="The local service could not load this page. No case or account changes were made.";
    $("#metrics").replaceChildren();
    $("#view-content").innerHTML='<div class="empty-state"><b>' + esc(error.message || "The local application is temporarily unavailable.") + '</b><span>Check that the local service and database are available, then retry.</span><br><button class="button secondary" type="button" id="retry-load">Retry</button></div>';
    $("#retry-load")?.addEventListener("click",()=>location.reload());
  }
}
async function signOut(){await api("/auth/logout",{method:"POST"}).catch(()=>{});location.assign("/login");}
async function submitRequest(event) {
  event.preventDefault();const form=event.currentTarget;const button=form.querySelector('[type="submit"]');button.disabled=true;
  try { const created=await api("/api/cases",{method:"POST",body:JSON.stringify({subject:form.elements.subject.value,request_text:form.elements.request_text.value})});showMessage($("#request-message"),"Request submitted as " + created.case_id + ". It remains pending human review.","success");form.reset();await loadData("user"); }
  catch(error){showMessage($("#request-message"),error.message,"error");}finally{button.disabled=false;}
}
async function adminChange(id,change,role) {
  try {const result=await api("/api/admin/accounts/"+encodeURIComponent(id),{method:"PATCH",body:JSON.stringify(change)});await loadData(role);showMessage($("#admin-message"),result.changed?"Account access updated and audit recorded.":"No change was needed.","success");}
  catch(error){showMessage($("#admin-message"),error.message,"error");}
}
document.addEventListener("DOMContentLoaded",start);
