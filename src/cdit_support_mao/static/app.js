const $ = (s, root=document) => root.querySelector(s);
let displayedWarning = "";
let signedInActor = {};
let feedbackByDecision = new Map();
const syntheticSamples = [
  ["IDNYC application", "I need the IDNYC application form."],
  ["Personal W-2", "I need a copy of my personal W-2."],
  ["Withholding change", "My withholding or deduction changed unexpectedly before this payroll closes."]
];

function decisionFeedback(decision, role) {
  const entries = feedbackByDecision.get(decision.decision_id) || [];
  const history = entries.map(entry => '<p class="helper"><strong>' +
    (entry.flagged ? "Flagged" : "Clear") + '</strong> ' + esc(entry.note) + '</p>').join("");
  if (role !== "admin") return history;
  return history + '<form class="stack-form" data-feedback="' + esc(decision.decision_id) +
    '"><label>Optional note<textarea name="note" maxlength="2000" rows="2"></textarea></label>' +
    '<label class="check-line"><input type="checkbox" name="flagged"' +
    (entries[0]?.flagged ? " checked" : "") + '> Flag this version</label>' +
    '<button class="button secondary" type="submit">Save feedback</button>' +
    '<span class="form-message" role="status"></span></form>';
}

function ticketReply(item) {
  if (!item.reply) return "";
  let links = "";
  if (item.reply_route === "routine_form") {
    links = '<a class="icon-button" href="/api/cases/' + encodeURIComponent(item.case_id) +
      '/form.pdf" title="Download requested PDF" aria-label="Download requested PDF">' + relayIcon("download") + '</a>';
  } else if (item.reply_route === "resource_link") {
    links = (Array.isArray(item.reply_links) ? item.reply_links : [{label: item.reply_reason || "Open resource", url: item.reply_url}])
      .filter(link => link && ( /^https:\/\//.test(link.url || "") || /^\/project-docs\/resources\/[A-Za-z0-9._-]+\.pdf$/.test(link.url || "") ))
      .map(link => '<a class="ticket-resource-link" href="' + esc(link.url) + '" target="_blank" rel="noopener noreferrer">' +
        relayIcon("external") + '<span>' + esc(link.label || "Open resource") + '</span></a>').join("");
  } else {
    links = '<strong>Routed for human review</strong>';
  }
  return '<div class="ticket-reply"><div><b>Assistant reply</b><p>' + esc(item.reply) +
    '</p>' + (links ? '<div class="ticket-resource-links">' + links + '</div>' : '') + '</div></div>';
}

function agentActivity(item, role) {
  if (item.record_kind !== "user_request") return "";
  const launch = role === "admin" && item.status === "submitted"
    ? '<form class="stack-form" data-run="' + esc(item.case_id) + '">' +
      '<label class="check-line"><input type="checkbox" name="authorize" required>' +
      'Authorize one billable Claude call</label><p class="helper">Synthetic requests only · max 2,000 characters · privacy screen blocks likely personal or sensitive details.</p>' +
      '<button class="button primary">▶ Run live Triage</button>' +
      '<span class="form-message" role="status"></span></form>' : "";
  return '<details class="agent-activity" data-run-details="' + esc(item.case_id) +
    '"><summary>' + relayIcon("activity") + ' Agent activity</summary>' +
    '<div data-run-results role="status"></div>' + launch + '</details>';
}

async function refreshRuns(panel) {
  const output = panel.querySelector("[data-run-results]");
  try {
    const records = await api("/api/cases/" + encodeURIComponent(panel.dataset.runDetails) + "/agent-runs");
    output.innerHTML = records.length ? records.map(run => {
      const result = run.result || {};
      const stageRows = result.stages || [["Coordinator", result.coordinator], ["Claude Triage", result.triage]]
        .filter(([,value]) => value).map(([name,status]) => ({name,status}));
      const stages = stageRows.map(stage => '<li><b>' + esc(stage.name) + '</b>: ' +
        esc(pretty(stage.status)) + (stage.decision_version ? ' · v' + esc(stage.decision_version) : '') +
        (stage.reasons?.length ? '<small> · ' + esc(stage.reasons.map(pretty).join(', ')) + '</small>' : '') + '</li>').join("");
      return '<article class="run-record">' + statusPill(run.status) + ' <small>' + esc(run.run_id) +
        '</small>' + (stages ? '<ul>' + stages + '</ul>' : '') +
        (run.provider_attempts !== undefined ? '<p>Provider attempts: ' + run.provider_attempts +
          ' · Validated response: ' + (result.validated_model_result ? "Yes" : "No") + '</p>' : '') +
        (result.usage ? '<p>' + esc(result.usage.model) + ' · ' +
          esc(result.usage.input_tokens) + ' input / ' + esc(result.usage.output_tokens) +
          ' output tokens</p>' : '') +
        (result.items?.length ? '<p>Request items: ' + result.items.map(item =>
          '#' + esc(item.index) + ' ' + esc(item.category)).join(' · ') + '</p>' : '') +
        (result.reason ? '<p>' + esc(pretty(result.reason)) + '</p>' : '') +
        (result.outcome_reason ? '<p>Outcome basis: ' + esc(pretty(result.outcome_reason)) + '</p>' : '') + '</article>';
    }).join("") : '<p class="helper">No agent run recorded.</p>';
  } catch (error) { output.textContent = error.message; }
}
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
function auditorPanel(item, decisions, categories, role) {
  const history = decisions.filter(d => d.case_id === item.case_id);
  const knownVersions = Object.fromEntries(history.reduce((latest, decision) => {
    latest.set(decision.item_id, Math.max(latest.get(decision.item_id) || 0, decision.decision_version)); return latest;
  }, new Map()));
  const current = history.filter(d => knownVersions[d.item_id] === d.decision_version);
  const past = history.filter(d => knownVersions[d.item_id] !== d.decision_version);
  const currentHtml = current.map(d => '<article class="decision-current"><strong>Current decision · v' +
    esc(d.decision_version) + '</strong><p>' + esc(d.category) + ' · ' + esc(pretty(d.urgency_band)) +
    '</p><p>' + esc(d.rationale) + '</p>' + decisionFeedback(d, role) + '</article>').join("");
  let historyHtml = past.length
    ? '<div class="auditor-history"><b>Version history</b>' + past.map(d => '<details class="decision-record"><summary>Item ' + esc(d.item_index) + ' of ' + esc(d.item_count) + ' · ' + esc(d.category) + ' / ' + esc(pretty(d.urgency_band)) + ' · v' + esc(d.decision_version) + '</summary><div class="decision-record-meta">' + esc(d.item_id) + ' · Destination: ' + esc(d.destination) + ' · Reviewer: ' + esc(d.reviewer_account_id) + ' · ' + esc(new Date(d.recorded_at).toLocaleString()) + '</div><p><b>Reason</b> ' + esc(d.rationale) + '</p><p><b>Evidence</b> ' + esc(d.evidence) + '</p><p><b>Conditions</b> ' + esc((d.conditions||[]).join("; ") || "None recorded") + '</p><p><b>Exceptions</b> ' + esc((d.exceptions||[]).join("; ") || "None recorded") + '</p><small>Case version ' + esc(d.case_version) + ' · Source ' + esc(d.source_id) + ' / ' + esc(d.source_version) + ' · Span ' + esc(d.source_start) + '–' + esc(d.source_end) + ' · Policy ' + esc(d.policy_version) + '</small>' + decisionFeedback(d, role) + '</details>').join('') + '</div>'
    : '<p class="helper">No human item decisions have been recorded for this case.</p>';
  historyHtml += history.filter(d => d.admin_override_reason).map(d => '<p class="helper"><b>Admin override reason (' + esc(d.reviewer_account_id) + '):</b> ' + esc(d.admin_override_reason) + '</p>').join('');
  historyHtml = past.length ? historyHtml : "";
  const canReview = item.status !== "closed" && (role === "admin" ||
    signedInActor.auditor && item.assigned_staff_account_id === signedInActor.account_id);
  if (!canReview) return currentHtml + historyHtml;
  const categoryOptions = categories.map(value => '<option value="' + esc(value) + '">' + esc(value) + '</option>').join('');
  return currentHtml + '<details class="auditor-panel"><summary>Review and version history <span>Auditor / Admin</span></summary>' + historyHtml +
    '<form class="auditor-decision-form stack-form" data-auditor-decision="' + esc(item.case_id) + '" data-known-versions="' + esc(JSON.stringify(knownVersions)) + '">' +
    '<p class="helper">Synthetic prototype only. Record the human decision for one linked item. This does not change ticket status, contact anyone, or execute a routing action. The case text span and case version are checked when saved.</p>' +
    '<input type="hidden" name="expected_case_version" value="' + esc(item.updated_at) + '"><input type="hidden" name="expected_previous_decision_version" value="0">' +
    '<div class="row-actions"><label>Item ID<input name="item_id" maxlength="128" required placeholder="ID from the reviewed item packet"></label><label>Item number<input name="item_index" type="number" min="1" max="8" value="1" required></label><label>Items in parent<input name="item_count" type="number" min="1" max="8" value="1" required></label></div>' +
    '<div class="row-actions"><label>Source span start<input name="source_start" type="number" min="0" value="0" required></label><label>Source span end<input name="source_end" type="number" min="1" max="12000" required></label><label>Category<select name="category" required><option value="">Choose category</option>' + categoryOptions + '</select></label></div>' +
    '<div class="row-actions"><label>Urgency band<select name="urgency_band" required><option value="">Choose band</option><option value="low">Low [P3]</option><option value="medium">Medium [P2]</option><option value="high">High [P1]</option></select></label><label>Proposed destination<input name="destination" maxlength="120" required placeholder="Human-selected synthetic destination"></label></div>' +
    '<div class="row-actions"><label>Source ID<input name="source_id" maxlength="128" required placeholder="Source referenced in the review packet"></label><label>Source version<input name="source_version" maxlength="64" required></label><label>Policy version<input name="policy_version" maxlength="64" required></label></div>' +
    (role === "admin" ? '<label>Admin override reason<textarea name="admin_override_reason" maxlength="500" rows="2" required placeholder="Why is Admin reviewing outside the assigned Staff workflow?"></textarea></label>' : '') +
    '<label>Reason / rationale<textarea name="rationale" maxlength="2000" rows="3" required></textarea></label><label>Evidence<textarea name="evidence" maxlength="2000" rows="3" required placeholder="Use synthetic evidence references or a brief source-linked explanation"></textarea></label>' +
    '<label>Conditions<textarea name="conditions" maxlength="1000" rows="2" placeholder="One condition per line (optional)"></textarea></label><label>Exceptions<textarea name="exceptions" maxlength="1000" rows="2" placeholder="One exception per line (optional)"></textarea></label>' +
    '<div class="form-bottom"><span class="helper">Reviewer identity and timestamp come from the authenticated session.</span><button class="button primary" type="submit">Record human decision</button></div><div class="form-message" role="status" aria-live="polite"></div></form></details>';
}
function assignmentPanel(item, role, staffAccounts=[], assignmentEvents=[]) {
  const current = item.assigned_staff_account_id || "";
  const label = item.assigned_staff_username || item.assigned_staff_account_id || "Unassigned";
  if (role !== "admin") return '<p class="helper">Assigned to you: ' + esc(label) + '</p>';
  const options = staffAccounts.filter(a => a.role === "staff" && a.status === "active").map(a =>
    '<option value="' + esc(a.account_id) + '"' + (a.account_id === current ? ' selected' : '') + '>' + esc(a.username) + ' (' + esc(a.account_id) + ')</option>'
  ).join("");
  const history = assignmentEvents.filter(e => e.case_id === item.case_id);
  const historyHtml = history.length ? '<details class="decision-record"><summary>Assignment history (' + history.length + ')</summary>' + history.map(e =>
    '<p>' + esc(pretty(e.action)) + ': ' + esc(e.previous_staff_username || "Unassigned") + ' → ' + esc(e.assigned_staff_username || "Unassigned") + ' · by ' + esc(e.actor_username || "synthetic seed") + ' · ' + esc(new Date(e.occurred_at).toLocaleString()) + '</p>'
  ).join("") + '</details>' : '';
  return '<form class="case-assignment-form" data-case-assignment="' + esc(item.case_id) + '"><label>Assigned Staff<select name="staff_account_id"><option value="">Unassigned</option>' + options + '</select></label><button class="button secondary" type="submit">Save assignment</button><span class="form-message" role="status" aria-live="polite"></span></form>' + historyHtml;
}
function cardForCase(item, role, decisions=[], categories=[], staffAccounts=[], assignmentEvents=[]) {
  const displayStatus = item.display_status || item.status;
  const kind = item.record_kind === "development_example" ? '<span class="role-pill">Development example</span>' : '<span class="role-pill">Client request</span>';
  const ownerLabel = item.record_kind === "development_example" ? "Fixture owner" : "Requester";
  const rationale = item.catalog_rationale ? '<p class="helper">Example context: ' + esc(item.catalog_rationale) + '</p>' : '';
  let controls = '';
  if (role === "user" && item.can_edit) {
    controls = '<form class="case-edit-form" data-case-edit="' + esc(item.case_id) + '"><label>Request title<input name="subject" maxlength="160" value="' + esc(item.subject) + '" required></label><label>Request details<textarea name="request_text" maxlength="12000" rows="3" required>' + esc(item.request_text) + '</textarea></label><button class="button secondary" type="submit">Save changes</button><span class="form-message" role="status"></span></form>';
  } else if (role === "user" && item.can_cancel) {
    controls = '<span class="helper">Editing is locked while support reviews this request.</span><button class="button secondary danger" type="button" data-case-cancel="' + esc(item.case_id) + '">' + relayIcon("close") + ' Request withdrawal</button>';
  } else if (signedInActor.auditor) {
    controls = auditorPanel(item, decisions, categories, role);
  } else if (role !== "user") {
    controls = assignmentPanel(item, role, staffAccounts, assignmentEvents) + '<form class="case-edit-form" data-case-edit="' + esc(item.case_id) + '"><label>Request title<input name="subject" maxlength="160" value="' + esc(item.subject) + '" required></label><label>Request details<textarea name="request_text" maxlength="12000" rows="3" required>' + esc(item.request_text) + '</textarea></label><div class="row-actions"><button class="button secondary" type="submit">Save case details</button>' + (item.allowed_next_statuses.length ? '<label class="status-control">Change status<select name="next_status" required><option value="">Choose status</option>' + statusOptions("", item.allowed_next_statuses) + '</select></label><button class="button primary" type="button" data-case-status="' + esc(item.case_id) + '">' + relayIcon("check") + ' Update status</button>' : '<span class="helper">Closed is terminal.</span>') + '</div><span class="form-message" role="status"></span></form>' + auditorPanel(item, decisions, categories, role);
  } else {
    controls = '<span class="helper">' + (item.closure_reason === "requester_cancelled_unresolved" ? "Cancelled by you as unresolved." : "This request is no longer editable.") + '</span>';
  }
  return '<article class="case-card"><div><div class="case-meta">' + kind + (role !== "user" ? '<span class="case-id">' + ownerLabel + ' ' + esc(item.owner_account_id) + '</span>' : '') + '</div><h3>' + esc(item.subject) + '</h3><p>' + esc(item.request_text) + '</p>' + rationale + ticketReply(item) + '<div class="case-meta"><span class="case-id">' + esc(item.case_id) + '</span>' + statusPill(displayStatus) + statusPill(item.urgency_band) + (item.withdrawal_requested_at && item.status !== "closed" ? '<span class="status-pill">Withdrawal requested</span>' : "") + (item.review_flag ?
    '<span class="review-flag">' + relayIcon("flag") + 'Close out or Review</span>' : "") + '<span>Created ' + esc(new Date(item.created_at).toLocaleString()) + '</span></div></div><div class="case-actions">' + controls + agentActivity(item,role) + '</div></article>';
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
  $("#actor-role").textContent = role === "user" ? "Client view" : role === "staff" ? (signedInActor.auditor ? "Auditor" : "Support operations") : "Privileged access";
  $("#avatar").className = "avatar " + role;
  $("#avatar").textContent = role[0].toUpperCase();
  const title = role === "user" ? "Your support desk" : role === "staff" ? (signedInActor.auditor ? "Auditor queue" : "Work queue") : "Access & system health";
  const crumb = role === "user" ? "CLIENT WORKSPACE / REQUESTS" : role === "staff" ? "SUPPORT OPERATIONS / WORKBENCH" : "ADMINISTRATION / OVERVIEW";
  const description = role === "user" ? "Send a request and follow its current status. Follow agent activity and human review from your ticket." : role === "staff" ? "Review synthetic requests, system evidence, and human-review handoffs." : "Manage synthetic accounts and inspect operational metadata. All changes are locally audited.";
  $("#page-title").textContent=title; $("#crumb").textContent=crumb; $("#page-description").textContent=description;
  $("#today").textContent=new Date().toLocaleDateString(undefined,{weekday:"short",month:"short",day:"numeric",year:"numeric"});
}
function renderMetrics(role, cases, accounts=[], alerts=[]) {
  const open = cases.filter(c=>["submitted","in_progress","waiting_on_customer","escalated"].includes(c.status)).length;
  const values = role === "user"
    ? [["YOUR REQUESTS",cases.length,"Visible to your account"],["IN REVIEW",open,"Status shown for your requests"],["HUMAN REVIEW","On","Eligible public forms can be fulfilled automatically"]]
    : role === "staff"
    ? [["CASES IN VIEW",cases.length,"Synthetic records only"],["NEEDS REVIEW",open,"Submitted or awaiting review"],["AGENT AUTHORITY","Draft","Approved public forms and human case controls"]]
    : [["SYNTHETIC ACCOUNTS",accounts.length,"User, Staff, Admin"],["ACTIVE CASES",cases.length,"Human-reviewed support queue"],["OPEN SESSION REQUESTS",alerts.filter(a=>a.review_status==="new").length,"Review only; no time extension"]];
  $("#metrics").innerHTML=values.map((x,i)=>'<article class="metric-card ' + (i===2 ? "accent" : "") + '"><span>' + esc(x[0]) + '</span><b>' + esc(x[1]) + '</b><small>' + esc(x[2]) + '</small></article>').join("");
}
function renderCases(cases, role, decisions=[], categories=[], staffAccounts=[], assignmentEvents=[]) {
  const root=$("#case-list");
  root.innerHTML=cases.length ? cases.map(c=>cardForCase(c,role,decisions,categories,staffAccounts,assignmentEvents)).join("") : empty(role==="user" ? "No requests yet" : "Queue is clear");
}
function requestForm() {
  return '<section class="panel" id="new-request"><div class="panel-heading"><div><div class="eyebrow">CREATE A CASE</div><h2>Tell us what you need</h2><p class="muted">Synthetic prototype only. Do not enter real personal, health, or customer information.</p></div><span class="panel-icon">＋</span></div><div class="resource-intro"><b>Personal documents:</b> This local build does not accept uploads. In a connected workflow, documents go only to the department responsible for the request, are used only for that department’s review, and are not retained in automated-processing or ticket records. Do not include real IDs, medical records, tax forms, or work-authorization documents in this prototype.</div><form id="request-form" class="stack-form"><label for="subject">Request title</label><input id="subject" name="subject" maxlength="160" placeholder="e.g. Report export access" required><label for="request-text">What happened or what do you need?</label><textarea id="request-text" name="request_text" maxlength="12000" rows="5" placeholder="Describe your synthetic support request." required></textarea><div class="form-bottom"><span class="helper">Synthetic examples only · 12,000 character maximum · See Forms & Resources in the footer</span><button class="button primary" type="submit">' + relayIcon("send") + ' Submit request</button></div><div id="request-message" class="form-message" role="status" aria-live="polite"></div></form></section>';
}
function renderStaffPanels(role) {
  const header = '<div class="section-head"><div><h2>' + (role==="user" ? "Recent requests" : "Case queue") + '</h2><p class="muted">' + (role==="user" ? "Only requests submitted by this account appear here." : "Manage the synthetic queue and the 80 tagged development examples. Agent outputs remain proposals.") + '</p></div>' + (role==="user" ? '<button class="button secondary" data-scroll="#new-request">＋ New request</button>' : '<button class="button secondary" id="refresh-cases" title="Refresh queue" aria-label="Refresh queue">' + relayIcon("reset") + '</button>') + '</div><div id="case-list" class="case-list" aria-live="polite"><div class="loading-card"><span class="spinner"></span> Loading synthetic cases…</div></div>';
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
  if (role === "admin" || signedInActor.auditor) {
    const feedback = await api("/api/auditor/feedback");
    feedbackByDecision = Map.groupBy(feedback, entry => entry.decision_id);
  }
  let decisions=[],categories=[];
  if(role!=="user") [decisions,categories]=await Promise.all([api("/api/auditor/decisions"),api("/api/auditor/taxonomy")]).then(([d,t])=>[d,t.categories||[]]);
  let accounts=[],alerts=[],assignmentEvents=[];
  if(role==="admin") [accounts,alerts,assignmentEvents]=await Promise.all([api("/api/admin/accounts"),api("/api/admin/session-extension-alerts"),api("/api/admin/case-assignment-events")]);
  const filters = $("#queue-filter");
  if (filters) {
    const redraw = () => {
      const criteria = Object.fromEntries(new FormData(filters));
      const query = criteria.search.toLowerCase().trim();
      const visible = cases.filter(item =>
        (!query || [item.subject, item.case_id, item.request_text].some(value => value.toLowerCase().includes(query))) &&
        (!criteria.status || item.status === criteria.status) &&
        (!criteria.band || item.urgency_band === criteria.band) &&
        (!criteria.category || item.category === criteria.category) &&
        (!criteria.from || item.created_at.slice(0, 10) >= criteria.from) &&
        (!criteria.to || item.created_at.slice(0, 10) <= criteria.to) &&
        (!criteria.assigned || item.assigned_staff_account_id === signedInActor.account_id) &&
        (!criteria.flag || (criteria.flag === "review" ? item.review_flag : !item.review_flag)));
      if (criteria.sort === "az") visible.sort((a,b) => a.subject.localeCompare(b.subject));
      renderCases(visible,role,decisions,categories,accounts,assignmentEvents);
    };
    filters.elements.status.innerHTML = '<option value="">Any</option>' +
      statusOptions(filters.elements.status.value, [...new Set(cases.map(c => c.status))].sort());
    filters.elements.category.innerHTML = '<option value="">Any</option>' +
      statusOptions(filters.elements.category.value, [...new Set(cases.map(c => c.category).filter(Boolean))].sort());
    filters.oninput = redraw;
    filters.onreset = () => queueMicrotask(redraw);
    redraw();
  } else renderCases(cases,role,decisions,categories,accounts,assignmentEvents);
  if(role==="admin"){ renderAccounts(accounts); renderAlerts(alerts); }
  if (signedInActor.auditor) {
    const directory = await api("/api/auditor/accounts");
    $("#auditor-directory").innerHTML = directory.map(account =>
      '<p>' + esc(account.username) + ' · ' +
      esc(account.role === "staff" && account.auditor_access ? "Auditor" : pretty(account.role)) +
      ' · ' + esc(pretty(account.status)) + '</p>').join("");
  }
  if(role!=="user") renderHealth(await api("/api/product-health"));
  renderMetrics(role,cases,accounts,alerts);
  if (role !== "user") mountRelayAnalytics(await api("/api/queue/activity"));
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
    signedInActor=actor; $("#actor-name").textContent=actor.username; setNav(role);
    if (setupRelayPresentation(role)) {
      $("#logout").addEventListener("click", signOut);
      return;
    }
    renderStaffPanels(role);
    if (role !== "user") {
      $("#case-list").insertAdjacentHTML("afterend", '<section class="panel" id="relay-analytics"></section>');
      $("#case-list").insertAdjacentHTML("beforebegin", `<details class="queue-filter-panel" open><summary aria-label="Queue filters" title="Queue filters">${relayIcon("filter")}</summary><form class="queue-filter" id="queue-filter" aria-label="Filter queue">
        <label><span>${relayIcon("search")} Search</span><input name="search" type="search"></label>
        <label>Status<select name="status"><option value="">Any</option></select></label>
        <label>Band<select name="band"><option value="">Any</option><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="unknown">Unknown</option></select></label>
        <label>Category<select name="category"><option value="">Any</option></select></label>
        <label>From<input type="date" name="from"></label><label>Through<input type="date" name="to"></label>
        <label>Flag<select name="flag"><option value="">Any</option><option value="review">Close out or Review</option><option value="none">No flag</option></select></label><label>Sort<select name="sort"><option value="">Recently updated</option><option value="az">A–Z</option></select></label>
        ${actor.auditor ? '<label class="check-line"><input type="checkbox" name="assigned" value="1"> My assigned work</label>' : ""}
        <button type="reset" class="icon-button" title="Reset filters" aria-label="Reset filters">${relayIcon("reset")}</button></form></details>`);
    }
    if (actor.auditor) {
      $("#view-content").insertAdjacentHTML("beforeend", '<section class="panel"><h2>Account directory</h2><div id="auditor-directory"></div></section>');
    }
    await loadData(role);
    if(role==="user") {
      const form = $("#request-form");
      form.addEventListener("submit", submitRequest);
      const examples = document.createElement("div");
      examples.className = "row-actions";
      examples.setAttribute("aria-label", "Synthetic examples");
      syntheticSamples.forEach(([label,text]) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "button secondary";
        button.textContent = label;
        button.addEventListener("click", () => {
          form.elements.subject.value = label;
          form.elements.request_text.value = text;
          form.elements.request_text.focus();
        });
        examples.append(button);
      });
      form.prepend(examples);
    }
    document.addEventListener("toggle", event => {
      if (event.target.matches("[data-run-details]") && event.target.open) refreshRuns(event.target);
    }, true);
    const refresh=$("#refresh-cases"); if(refresh)refresh.addEventListener("click",()=>loadData(role).catch(e=>showMessage($("#admin-message"),e.message,"error")));
    document.addEventListener("click", async e=>{
      const scroll=e.target.closest("[data-scroll]"); if(scroll){e.preventDefault();document.querySelector(scroll.dataset.scroll)?.scrollIntoView({behavior:"smooth"});}
      const roleSave=e.target.closest("[data-role-save]"); if(roleSave){const id=roleSave.dataset.roleSave;const select=document.querySelector('[data-role-select="' + id + '"]');if(select.value)await adminChange(id,{role:select.value},role);else showMessage($("#admin-message"),"Choose a role first.");}
      const statusSave=e.target.closest("[data-status-save]"); if(statusSave){const id=statusSave.dataset.statusSave;const select=document.querySelector('[data-status-select="' + id + '"]');if(select.value)await adminChange(id,{status:select.value},role);else showMessage($("#admin-message"),"Choose an access status first.");}
      const review=e.target.closest("[data-alert-review]"); if(review)try{await api("/api/admin/session-extension-alerts/"+encodeURIComponent(review.dataset.alertReview)+"/review",{method:"PATCH"});await loadData(role);}catch(err){showMessage($("#admin-message"),err.message,"error");}
    });
    document.addEventListener("input", e=>{
      const itemId=e.target.closest('input[name="item_id"]');
      if(!itemId)return;
      const form=itemId.closest("form[data-auditor-decision]");
      try {
        const versions=JSON.parse(form.dataset.knownVersions || "{}");
        form.elements.expected_previous_decision_version.value=String(versions[itemId.value.trim()] || 0);
      } catch { form.elements.expected_previous_decision_version.value="0"; }
    });
    document.addEventListener("click", async e=>{
      const cancel=e.target.closest("[data-case-cancel]");
      if(cancel){
        if(!window.confirm("Send a withdrawal request to support? The ticket will stay open for review."))return;
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
      const run = e.target.closest("form[data-run]");
      if (run) {
        e.preventDefault();
        const message = run.querySelector(".form-message");
        const button = run.querySelector("button");
        button.disabled = true;
        showMessage(message, "Running live Triage…");
        try {
          const result = await api("/api/cases/" + encodeURIComponent(run.dataset.run) + "/agent-runs", {
            method: "POST", body: JSON.stringify({authorize_billable_call: run.elements.authorize.checked})
          });
          await refreshRuns(run.closest("[data-run-details]"));
          showMessage(message, "Run recorded: " + pretty(result.status) + ".");
          run.elements.authorize.checked = false;
        } catch (error) { showMessage(message, error.message, "error"); }
        finally { button.disabled = false; }
        return;
      }
      const feedback = e.target.closest("form[data-feedback]");
      if (feedback) {
        e.preventDefault();
        const message = feedback.querySelector(".form-message");
        try {
          await api("/api/admin/auditor-decisions/" + encodeURIComponent(feedback.dataset.feedback) + "/feedback", {
            method: "POST", body: JSON.stringify({note:feedback.elements.note.value, flagged:feedback.elements.flagged.checked})
          });
          await loadData(role);
        } catch (error) { showMessage(message, error.message, "error"); }
        return;
      }
      const assignmentForm=e.target.closest("form[data-case-assignment]");
      if(assignmentForm){
        e.preventDefault();const message=assignmentForm.querySelector(".form-message");
        const staffAccountId=assignmentForm.elements.staff_account_id.value || null;
        try{const result=await api("/api/admin/cases/"+encodeURIComponent(assignmentForm.dataset.caseAssignment)+"/assignment",{method:"PATCH",body:JSON.stringify({staff_account_id:staffAccountId})});await loadData(role);showMessage($("#admin-message")||message,result.changed?"Case assignment saved and logged.":"No assignment change was needed.","success");}
        catch(error){showMessage(message,error.message,"error");}
        return;
      }
      const auditorForm=e.target.closest("form[data-auditor-decision]");
      if(auditorForm){
        e.preventDefault();const form=auditorForm;const message=form.querySelector(".form-message");const values=Object.fromEntries(new FormData(form).entries());
        const lines=name=>String(values[name]||"").split(/\r?\n/).map(x=>x.trim()).filter(Boolean);
        const payload={...values,item_index:Number(values.item_index),item_count:Number(values.item_count),expected_previous_decision_version:Number(values.expected_previous_decision_version),source_start:Number(values.source_start),source_end:Number(values.source_end),conditions:lines("conditions"),exceptions:lines("exceptions")};
        delete payload.conditions_text;delete payload.exceptions_text;payload.conditions=lines("conditions");payload.exceptions=lines("exceptions");
        try {
          const casePath = "/api/cases/" + encodeURIComponent(form.dataset.auditorDecision);
          const decision = await api(casePath + "/items/auditor-decisions", {method:"POST",body:JSON.stringify(payload)});
          try {
            await api(casePath + "/resume-review", {method:"POST",body:JSON.stringify({decision_id:decision.decision_id})});
          } catch (error) {
            showMessage(message, "Decision saved. Review remains open: " + error.message, "error");
            return;
          }
          const caseId = form.dataset.auditorDecision;
          await loadData(role);
          const activity = [...document.querySelectorAll("[data-run-details]")].find(panel => panel.dataset.runDetails === caseId);
          if (activity) activity.open = true;
        } catch(error) { showMessage(message,error.message,"error"); }
        return;
      }
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
  try { const created=await api("/api/cases",{method:"POST",body:JSON.stringify({subject:form.elements.subject.value,request_text:form.elements.request_text.value})});showMessage($("#request-message"),created.status === "resolved" ? "Resolved. The requested document or official resource is available in your ticket." :
    "Request submitted as " + created.case_id + ". It remains open for review.","success");form.reset();await loadData("user"); }
  catch(error){showMessage($("#request-message"),error.message,"error");}finally{button.disabled=false;}
}
async function adminChange(id,change,role) {
  try {const result=await api("/api/admin/accounts/"+encodeURIComponent(id),{method:"PATCH",body:JSON.stringify(change)});await loadData(role);showMessage($("#admin-message"),result.changed?"Account access updated and audit recorded.":"No change was needed.","success");}
  catch(error){showMessage($("#admin-message"),error.message,"error");}
}
document.addEventListener("DOMContentLoaded",start);
