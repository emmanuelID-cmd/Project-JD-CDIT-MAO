/* Shared presentation navigation and accessible ActionRelay icon vocabulary. */
const actionrelayPaths = Object.freeze({
  back: "M19 12H5m7-7-7 7 7 7",
  demo: "m8 5 12 7-12 7z",
  story: "M3 5h18v14H3zM7 9h10M7 13h7",
  search: "M21 21l-5-5m2-5a7 7 0 1 1-14 0 7 7 0 0 1 14 0Z",
  filter: "M3 5h18l-7 8v5l-4 2v-7Z",
  reset: "M3 12a9 9 0 1 1 3 7M3 6v6h6",
  download: "M12 3v12m-5-5 5 5 5-5M5 16v4h14v-4",
  external: "M14 3h7v7m0-7L10 14m8-1v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6",
  flag: "M5 21V4m0 1c5-5 9 4 15 0v10c-6 4-10-5-15 0",
  activity: "M2 12h5l3-7 4 14 3-7h5",
  check: "m5 12 4 4L19 6",
  close: "M6 6l12 12M18 6 6 18",
  next: "m9 5 7 7-7 7",
  previous: "m15 5-7 7 7 7",
  send: "m3 4 18 8-18 8 4-8-4-8Zm4 8h14",
  logout: "M10 4H4v16h6m3-4 4-4-4-4m-5 4h12",
});

function relayIcon(name) {
  return '<svg class="relay-icon" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" ' +
    'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="' +
    actionrelayPaths[name] + '"/></svg>';
}

const relayDocs = "/project-docs/";
const relayDemo = relayDocs + "presentations/ActionRelay-review/";
const relayResources = [
  ["Company directory — synthetic contacts", "resources/synthetic-company-directory.pdf"],
  ["Workplace guide — synthetic sample", "resources/synthetic-workplace-guide.pdf"],
  ["Blank vacation request — synthetic form", "resources/synthetic-vacation-request.pdf"],
  ["Blank workplace complaint — synthetic form", "resources/synthetic-workplace-complaint.pdf"],
  ["Weekly timesheet — synthetic PDF", "presentations/ActionRelay/ActionRelay-Sample-Weekly-Timesheet.pdf"],
  ["Shift patterns A–D — synthetic PDF", "presentations/ActionRelay/ActionRelay-Sample-Shift-Options-and-Change-Request.pdf"],
  ["IRS 2026 Form W-4 — official PDF", "https://www.irs.gov/pub/irs-pdf/fw4.pdf", "leave"],
  ["DOL FMLA WH-380-E — employee health condition", "https://www.dol.gov/sites/dolgov/files/WHD/legacy/files/wh-380-e.pdf", "leave"],
  ["DOL FMLA WH-380-F — family member health condition", "https://www.dol.gov/sites/dolgov/files/WHD/legacy/files/wh-380-f.pdf", "leave"],
  ["NYS PFL family-care packet — PFL-1, PFL-3, PFL-4", "https://www.wcb.ny.gov/content/main/forms/PFLDocs/PFL3.pdf", "leave"],
  ["NYS PFL bonding packet — PFL-1, PFL-2", "https://www.wcb.ny.gov/content/main/forms/PFLDocs/PFL2.pdf", "leave"],
  ["NYS Paid Family Leave form packages", "https://paidfamilyleave.ny.gov/forms", "leave"],
  ["IDNYC application materials", "https://www.nyc.gov/site/idnyc/card/application-materials.page"],
];

const relayProjectResources = [
  ["Expanded field guide", "architecture/actionrelay-field-guide.html"],
  ["Standalone architecture SVG", "architecture/actionrelay-architecture.svg"],
  ["Technical architecture notes", "architecture/ActionRelay-Architecture.md"],
  ["Case scenarios", "requirements/CASE-SCENARIOS.md"],
  ["User needs and priorities", "requirements/PRD-USER-NEEDS-AND-USE-CASE-PRIORITIES.md"],
  ["Implementation phases", "planning/AGENT-IMPLEMENTATION-PHASE-PLAN.md"],
  ["Deferred decisions", "planning/DEFERRED-DECISIONS.md"],
  ["Local app and authentication plan", "planning/phase/undecided/unassigned/LOCAL-APP-DATA-AUTH-PLAN.md"],
  ["Original architecture diagram", "artifacts/cdit-support-mao-architecture-prd-v2.jpg"],
  ["Original field guide", "artifacts/cdit-support-mao-field-guide.html"],
  ["Claude model documentation", "https://platform.claude.com/docs/en/models/sonnet-5-5/overview"],
  ["Official IDNYC materials", "https://www.nyc.gov/site/idnyc/card/application-materials.page"],
];

const relaySlides = [
  ["Employee support starts with a request", "A colleague needs a blank employment form. Another reports an unexpected payroll change. Both need a clear next step, but only one is a straightforward document request."],
  ["CDIT’s mission and its people", "CDIT has delivered technology and management services across Defense, Health, Civil, and Intelligence since 2003. Reliable employee support helps the people behind that mission get answers and return their attention to customer work.",
   [["CDIT: official company profile", "https://www.cditsolutions.com/"]]],
  ["A documented HR service gap", "In Arlington Public Schools’ 2025 HR audit, 26% of 1,539 survey respondents agreed or strongly agreed HR was responsive. In one sample, 23 of 412 closed tickets (5.6%) lacked recorded evidence of a response or supporting documentation. A separate benefits sample found 68 of 137 closed tickets (about 50%) lacked notes or an explanation.",
   [["Arlington Public Schools: 2025 HR audit report", "https://www.apsva.us/wp-content/uploads/sites/57/2025/09/Final-Human-Resources-Audit-Report.pdf"]]],
  ["What the audit numbers mean", "These are Arlington Public Schools findings, not CDIT data or an industry-wide rate. Missing documentation does not prove no one responded, and the audit did not count never-started tickets. It shows why clear ownership, status, follow-up, and an audit trail matter."],
  ["Why six distinct responsibilities", "Coordinator routes the case. Triage identifies the request and urgency. Knowledge checks approved evidence. Troubleshooting handles supported steps. Escalation identifies when a person must decide. Documentation records the evidence and action. Each responsibility feeds the next, with human review where authority or evidence requires it."],
  ["Automate the clear request; route the uncertain one", "For a verified, blank public form, ActionRelay can locate the official document, make it available on the ticket, and mark the request Resolved. A personal W-2 or an unexpected withholding change stays open for the appropriate human review. Resolution does not mean the ticket is Closed."],
  ["Measure speed before claiming savings", "The target is to move a verified, routine form request from hours of waiting to a response in minutes or seconds. We do not yet have CDIT ticket data or a validated manual-time baseline. Report synthetic run times separately, then compare like-for-like human and automated handling before claiming time saved."],
  ["ActionRelay walkthrough", "The interface and demo use synthetic people and cases. Follow the requester, staff, auditor, and admin perspectives; then watch the low-risk form path and the human-review path. The demo is a workflow illustration, not CDIT production data."]
];

function setupRelayPresentation(role) {
  const shell = document.querySelector("#view-content");
  const view = location.pathname === "/app/resources" ? "resources" : new URLSearchParams(location.search).get("view");
  const base = "/app/" + role;
  const nav = document.querySelector("#side-nav");
  const links = document.createElement("nav");
  links.className = "presentation-nav";
  links.setAttribute("aria-label", "Presentation");
  links.innerHTML = [["storyboard","story","Storyboard"], ["demo","demo","Demo"]].map(([id,icon,label]) =>
    '<a class="nav-item presentation-' + id + '" href="' + base + '?view=' + id + '"' +
    (view === id ? ' aria-current="page"' : "") + ">" + relayIcon(icon) + label + "</a>").join("");
  nav.after(links);
  document.querySelector("#copyright-year").textContent = new Date().getFullYear();
  document.querySelector("#resource-links").innerHTML = '<div class="resource-group-title">Forms and employee resources</div>' +
    relayResources.map(([label,path,kind]) =>
    '<a href="' + (path.startsWith("https://") ? path : relayDocs + path) +
    '" target="_blank" rel="noopener"' + (kind === "leave" ? ' data-leave-form="true"' : "") + '>' + label + '</a>').join("") +
    '<div class="resource-group-title">Project documents</div>' +
    relayProjectResources.map(([label,path]) => '<a href="' + (path.startsWith("https://") ? path : relayDocs + path) +
      '" target="_blank" rel="noopener">' + label + '</a>').join("");
  document.querySelector("#resource-links").addEventListener("click", event => {
    const link = event.target.closest('a[data-leave-form="true"]');
    if (link && !window.confirm("These forms apply only to some leave situations. Speak with your employer or HR first. Additional documentation may be needed, and eligibility is decided by the appropriate employer or insurer. Continue to the official government form?")) event.preventDefault();
  });
  document.querySelector("#logout").innerHTML = relayIcon("logout");
  if (!["storyboard","demo","resources"].includes(view)) return false;
  for (const anchor of nav.querySelectorAll('a[href^="#"]')) {
    anchor.href = base + anchor.getAttribute("href");
  }
  nav.querySelector(".active")?.classList.remove("active");
  document.querySelector("#page-title").textContent = view === "demo" ? "Demo" : view === "resources" ? "Forms & Resources" : "Storyboard";
  document.querySelector("#page-description").textContent =
    view === "demo" ? "Follow the synthetic workflow in either playback edition." : view === "resources" ? "Find the forms and reference documents available in this synthetic workspace." : "The CDIT support problem and the design behind ActionRelay.";
  document.querySelector("#metrics").hidden = true;
  const back = '<a class="icon-button return-workspace" href="' + base +
    '" aria-label="Back to workspace" title="Back to workspace">' + relayIcon("back") + '</a>';
  if (view === "resources") {
    shell.innerHTML = back + '<section class="panel resource-catalog"><div class="panel-heading"><div><div class="eyebrow">DOWNLOADS &amp; REFERENCES</div><h2>Available forms and resources</h2><p class="muted">Synthetic employee forms are examples for this prototype. Official forms link directly to their issuing government source.</p></div><span class="panel-icon">⇩</span></div><div class="resource-intro"><b>Personal documents:</b> This synthetic build does not accept or transmit personal documents. In a connected workflow, documents would be delivered only to the department responsible for the request and used only for that department’s review. The automated system does not retain personal documents.</div><div id="resource-catalog-links"></div></section>';
    document.querySelector("#resource-catalog-links").innerHTML = document.querySelector("#resource-links").innerHTML;
    document.querySelector("#resource-catalog-links").addEventListener("click", event => { const link = event.target.closest('a[data-leave-form="true"]'); if (link && !window.confirm("These forms apply only to some leave situations. Speak with your employer or HR first. Additional documentation may be needed, and eligibility is decided by the appropriate employer or insurer. Continue to the official government form?")) event.preventDefault(); });
  } else if (view === "demo") {
    shell.innerHTML = back + '<div class="demo-modes" aria-label="Playback edition">' +
      '<button class="button secondary" type="button" data-edition="continuous" aria-pressed="true">Continuous</button>' +
      '<button class="button secondary" type="button" data-edition="presenter" aria-pressed="false">Presenter</button>' +
      '<a class="button secondary" id="full-demo" target="_blank" rel="noopener">Open full-screen</a></div>' +
      '<iframe class="embedded-demo" title="ActionRelay simulated walkthrough" ' +
      'sandbox="allow-scripts allow-downloads allow-popups allow-popups-to-escape-sandbox"></iframe>';
    const editions = {continuous:"actionrelay-demo.html",presenter:"actionrelay-demo-beats.html"};
    const choose = edition => {
      const source = relayDemo + editions[edition];
      shell.querySelector("iframe").src = source;
      shell.querySelector("#full-demo").href = source;
      for (const button of shell.querySelectorAll("[data-edition]")) {
        button.setAttribute("aria-pressed", button.dataset.edition === edition);
      }
    };
    shell.addEventListener("click", event => {
      const button = event.target.closest("[data-edition]");
      if (button && button.getAttribute("aria-pressed") !== "true") choose(button.dataset.edition);
    });
    choose("continuous");
  } else {
    shell.innerHTML = back + '<section class="panel storyboard" aria-label="Storyboard slides">' +
      '<div id="story-slide" aria-live="polite"></div><div class="story-actions">' +
      '<button type="button" class="icon-button" data-slide="-1" title="Previous slide" aria-label="Previous slide">' +
      relayIcon("previous") + '</button><span id="story-progress"></span>' +
      '<button type="button" class="icon-button" data-slide="1" title="Next slide" aria-label="Next slide">' +
      relayIcon("next") + '</button></div></section>';
    let index = 0;
    const draw = () => {
      const [title,body,sources=[]] = relaySlides[index];
      shell.querySelector("#story-slide").innerHTML = "<h2>" + title + "</h2><p>" + body + "</p>" +
        sources.map(([label,url]) => '<a href="' + url + '" target="_blank" rel="noopener">' + label + '</a>').join("") +
        (index === relaySlides.length - 1 ? '<a class="button primary" href="' + base +
          '?view=demo">' + relayIcon("demo") + 'Open Demo</a>' : "");
      shell.querySelector("#story-progress").textContent = (index + 1) + " / " + relaySlides.length;
      shell.querySelector('[data-slide="-1"]').disabled = index === 0;
      shell.querySelector('[data-slide="1"]').disabled = index === relaySlides.length - 1;
    };
    shell.addEventListener("click", event => {
      const button = event.target.closest("[data-slide]");
      if (button) {
        index = Math.max(0, Math.min(relaySlides.length - 1, index + Number(button.dataset.slide)));
        draw();
      }
    });
    draw();
  }
  return true;
}
