/* Scoped analytics computed from persisted lifecycle events. */
const relayStatusColors = Object.freeze({
  submitted:"#70b9ff", in_progress:"#bf9df9", waiting_on_customer:"#f4b76d",
  under_investigation:"#f681a6", escalated:"#fb776c", resolved:"#70e2ba", closed:"#9faec3",
});
const relayDay = 86_400_000;
const isoDay = value => new Date(value).toISOString().slice(0,10);
const dayTime = day => Date.parse(day + "T00:00:00Z");

function mountRelayAnalytics(data) {
  const root = document.querySelector("#relay-analytics");
  if (!root) return;
  const now = new Date();
  const year = now.getUTCFullYear();
  const from = (year - 3) + "-01-01";
  const through = isoDay(now);
  root.innerHTML = `<div class="panel-heading"><div><h2>Queue analytics</h2><p class="muted">Scoped synthetic cases and recorded events.</p></div>${relayIcon("activity")}</div>
    <form id="analytics-controls" class="queue-filter">
      <label>From<input type="date" name="from" value="${from}" min="${from}" max="${through}"></label>
      <label>Through<input type="date" name="through" value="${through}" min="${from}" max="${through}"></label>
      <label>Interval<select name="unit"><option value="day">Day</option><option value="month">Month</option><option value="year">Year</option></select></label>
      <label>Jump to date<input type="date" name="jump" value="${through}" min="${from}" max="${through}"></label>
      <button type="button" class="icon-button" data-activity-step="-1" title="Previous period" aria-label="Previous period">${relayIcon("previous")}</button>
      <button type="button" class="icon-button" data-activity-step="1" title="Next period" aria-label="Next period">${relayIcon("next")}</button>
    </form>
    <div id="relay-metrics" class="analytics-metrics"></div><div id="relay-comparison"></div>
    <h3 id="activity-year">Ticket activity</h3><p id="activity-detail" role="status"></p>
    <div class="activity-scroll" tabindex="0" aria-label="Scroll ticket activity timeline"></div>
    <p class="muted">Blue: received · Green: resolved · Gray: closed. Counts are events within the selected range.</p>`;
  const form = root.querySelector("form");
  const view = root.querySelector(".activity-scroll");
  const dates = form.elements;
  const caseMap = new Map(data.cases.map(item => [item.case_id,item]));
  const timelineEvents = [
    ...data.cases.map(item => ({case_id:item.case_id, at:item.created_at, kind:"received"})),
    ...data.events.filter(event => event.status === "resolved" || event.status === "closed")
      .map(event => ({...event, kind:event.status})),
  ];
  let buckets = [], unit = "day";
  const sources = data.events.reduce((byCase,event) => {
    const events = byCase.get(event.case_id) || [];
    events.push(event);
    byCase.set(event.case_id,events);
    return byCase;
  },new Map());

  function snapshot(cutoff) {
    const counts = Object.fromEntries(Object.keys(relayStatusColors).map(key => [key,0]));
    for (const item of data.cases) {
      if (item.created_at.slice(0,10) > cutoff) continue;
      const last = sources.get(item.case_id)?.filter(event => event.at.slice(0,10) <= cutoff).at(-1);
      counts[last?.status || "submitted"]++;
    }
    return counts;
  }

  function wheel(counts, label) {
    const total = Object.values(counts).reduce((sum,count) => sum + count,0);
    const radius = 44, circumference = Math.PI * radius * 2;
    let offset = 0;
    const values = Object.entries(counts).map(([status,count]) => {
      if (!count) return "";
      const share = count / total, length = share * circumference;
      const angle = (offset + length / 2) / circumference * 2 * Math.PI;
      const point = [64 + radius * Math.sin(angle),64 - radius * Math.cos(angle)];
      const arc = '<circle cx="64" cy="64" r="44" fill="none" stroke="' + relayStatusColors[status] +
        '" stroke-width="23" stroke-dasharray="' + length + ' ' + circumference + '" stroke-dashoffset="' +
        (-offset) + '" transform="rotate(-90 64 64)"><title>' + pretty(status) + ': ' + count +
        ' (' + (share * 100).toFixed(1) + '%)</title></circle>';
      offset += length;
      return arc + (share >= .08 ? '<text x="' + point[0] + '" y="' + (point[1]+3) +
        '" text-anchor="middle" fill="#091421" font-size="9" font-weight="800" pointer-events="none">' +
        Math.round(share*100) + '%</text>' : "");
    });
    // Draw labels above all arcs so adjacent segments never obscure their text.
    const arcs = values.map(value => value.split("</circle>")[0] + (value ? "</circle>" : "")).join("");
    const labels = values.map(value => value.split("</circle>")[1] || "").join("");
    return '<figure class="status-wheel"><figcaption>' + label + '</figcaption><svg role="img" ' +
      'aria-label="' + label + ' status snapshot, ' + total + ' cases" viewBox="0 0 128 128">' +
      '<circle cx="64" cy="64" r="44" fill="none" stroke="#28364b" stroke-width="23"/>' + arcs + labels +
      '<text x="64" y="70" text-anchor="middle" fill="#f1f5ff" font-size="20">' + total + '</text></svg></figure>';
  }

  function compare(end) {
    const target = new Date(dayTime(end));
    const priorYear = target.getUTCFullYear() - 1;
    const lastDay = new Date(Date.UTC(priorYear, target.getUTCMonth()+1, 0)).getUTCDate();
    const prior = isoDay(Date.UTC(priorYear,target.getUTCMonth(),Math.min(lastDay,target.getUTCDate())));
    const previous = snapshot(prior), current = snapshot(end);
    const rows = Object.keys(current).map(key => {
      const change = current[key] - previous[key];
      const relative = previous[key] ? (100 * change / previous[key]).toFixed(1) + "%" : "No baseline";
      return '<tr><th scope="row"><svg aria-hidden="true" width="12" height="12"><circle cx="6" cy="6" r="5" fill="' +
        relayStatusColors[key] + '"/></svg> ' + pretty(key) + '</th><td>' + previous[key] + '</td><td>' +
        current[key] + '</td><td>' + (change > 0 ? "+" : "") + change + '</td><td>' + relative + '</td></tr>';
    }).join("");
    root.querySelector("#relay-comparison").innerHTML = '<h3>Status at cutoff</h3><div class="wheel-comparison">' +
      wheel(previous,prior) + wheel(current,end) + '<div class="table-wrap"><table class="data-table"><thead><tr>' +
      '<th scope="col">Status</th><th scope="col">Prior</th><th scope="col">Current</th>' +
      '<th scope="col">Change</th><th scope="col">Change %</th></tr></thead><tbody>' + rows +
      '</tbody></table></div></div>';
  }

  function metrics(first,last) {
    const inRange = date => date.slice(0,10) >= first && date.slice(0,10) <= last;
    const resolved = data.events.filter(event => event.status === "resolved" && inRange(event.at));
    const automatic = resolved.filter(event => event.kind === "automatic_fulfillment");
    const human = resolved.filter(event => event.kind !== "automatic_fulfillment");
    const handled = new Set([...data.handoffs.filter(event => inRange(event.at)).map(event => event.case_id),
                             ...human.map(event => event.case_id)]);
    const duration = events => {
      const elapsed = events.map(event => (Date.parse(event.at) - Date.parse(caseMap.get(event.case_id).created_at))/3600000)
        .filter(value => value >= 0);
      return elapsed.length ? (elapsed.reduce((sum,value) => sum + value,0) / elapsed.length).toFixed(2) + " h" : "—";
    };
    const backlog = data.cases.filter(item => item.status === "resolved").length;
    root.querySelector("#relay-metrics").innerHTML = [
      ["Automatic fulfillment",automatic.length,duration(automatic) + " mean to resolve"],
      ["Human resolutions",human.length,duration(human) + " mean to resolve"],
      ["Cases with human handling",handled.size,"Handoffs or human resolution in range"],
      ["Awaiting closure",backlog,"Current resolved cases"],
    ].map(([name,value,note]) => '<div class="metric-card"><span>' + name + '</span><b>' + value +
      '</b><small>' + note + '</small></div>').join("");
  }

  const keyFor = date => date.slice(0, unit === "day" ? 10 : unit === "month" ? 7 : 4);
  function pin(index, scroll=false) {
    const bucket = buckets[index];
    if (!bucket) return;
    const [key,counts] = bucket;
    root.querySelector("#activity-year").textContent = "Ticket activity · " + key.slice(0,4);
    root.querySelector("#activity-detail").textContent = key + " · Received " + counts.received +
      " · Resolved " + counts.resolved + " · Closed " + counts.closed;
    const marker = view.querySelector("line[data-marker]");
    marker.setAttribute("x1",20 + index*24);
    marker.setAttribute("x2",20 + index*24);
    if (scroll) view.scrollLeft = index*24 - view.clientWidth/2;
  }

  function draw() {
    const first = dates.from.value || from, last = dates.through.value || through;
    if (first > last || first < from || last > through) {
      root.querySelector("#activity-detail").textContent = "Choose a valid date range.";
      return;
    }
    unit = dates.unit.value;
    const counts = new Map();
    for (let day=dayTime(first); day<=dayTime(last); day+=relayDay) {
      const key = keyFor(isoDay(day));
      if (!counts.has(key)) counts.set(key,{received:0,resolved:0,closed:0});
    }
    for (const event of timelineEvents) {
      const day = event.at.slice(0,10);
      if (day >= first && day <= last) counts.get(keyFor(day))[event.kind]++;
    }
    buckets = [...counts];
    const width = Math.max(240,40+buckets.length*24);
    const peak = Math.max(1,...buckets.flatMap(([,values])=>Object.values(values)));
    const lines = [["received","#70b9ff"],["resolved","#70e2ba"],["closed","#9faec3"]].map(([status,color]) =>
      '<polyline fill="none" stroke="' + color + '" stroke-width="2" points="' +
      buckets.map(([,values],i) => (20+i*24) + "," + (108-values[status]*85/peak)).join(" ") + '"/>').join("");
    const ticks = buckets.map(([key],i) => i % (unit === "day" ? 7 : 1) ? "" :
      '<text x="' + (20+i*24) + '" y="133" text-anchor="middle" fill="#bdcbe0" font-size="10">' +
      (unit === "day" ? key.slice(5) : key) + '</text>').join("");
    view.innerHTML = '<svg width="' + width + '" height="146" aria-label="Received, resolved, and closed activity" role="img">' +
      '<path d="M20 108H' + (width-20) + '" stroke="#47627f"/>' + lines + ticks +
      '<line data-marker x1="20" x2="20" y1="12" y2="109" stroke="#fff" stroke-dasharray="4 4"/></svg>';
    dates.jump.min = first;
    dates.jump.max = last;
    dates.jump.value = last;
    metrics(first,last);
    compare(last);
    pin(buckets.length-1,true);
  }
  form.addEventListener("change", event => {
    if (event.target === dates.jump) pin(buckets.findIndex(([key])=>key === keyFor(dates.jump.value)),true);
    else draw();
  });
  form.addEventListener("click", event => {
    const button = event.target.closest("[data-activity-step]");
    if (button && unit !== "year") view.scrollBy({left:Number(button.dataset.activityStep)*24*(unit === "day" ? 7 : 1)});
  });
  view.addEventListener("pointermove", event => {
    const svg = view.querySelector("svg");
    if (svg) pin(Math.max(0,Math.min(buckets.length-1,Math.floor((event.clientX-svg.getBoundingClientRect().left-20)/24))));
  });
  draw();
}
