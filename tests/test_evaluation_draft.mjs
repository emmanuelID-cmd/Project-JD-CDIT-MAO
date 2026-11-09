import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const repo = path.resolve(import.meta.dirname, '..');
const draftPath = path.join(repo, 'synthetic_data/evaluation_draft/v1/cases.json');
const catalogPath = path.join(repo, 'docs/requirements/CASE-SCENARIOS.md');
const data = JSON.parse(fs.readFileSync(draftPath, 'utf8'));
const normalize = (s) => s.normalize('NFKC').toLowerCase().replace(/\s+/g, ' ').trim();

function walk(dir) {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const full = path.join(dir, entry.name);
    return entry.isDirectory() ? walk(full) : [full];
  });
}
function collectLongStrings(value, out = []) {
  if (typeof value === 'string') { if (value.length > 30) out.push(value); }
  else if (Array.isArray(value)) value.forEach((v) => collectLongStrings(v, out));
  else if (value && typeof value === 'object') Object.values(value).forEach((v) => collectLongStrings(v, out));
  return out;
}

test('draft has 100 unique, explicitly unapproved synthetic cases', () => {
  assert.equal(data.case_count, 100);
  assert.equal(data.cases.length, 100);
  assert.equal(new Set(data.cases.map((c) => c.case_id)).size, 100);
  assert.equal(data.approval.approved, false);
  assert.equal(data.approval.scoring_authorized, false);
  assert.equal(data.scope.not_scored, true);
  for (const c of data.cases) {
    assert.match(c.case_id, /^SYN-EVAL-\d{3}$/);
    assert.equal(c.record_status, 'DRAFT_NOT_APPROVED');
    assert.equal(c.synthetic_only, true);
    assert.equal(c.split, 'label_review_draft');
    assert.ok(Array.isArray(c.items) && c.items.length > 0);
    assert.ok(Array.isArray(c.must_pass_gate_tags) && c.must_pass_gate_tags.length > 0);
    for (const item of c.items) {
      assert.equal(item.triage_proposal.urgency, 'unknown', `${c.case_id}: current A2 urgency must remain unknown`);
      assert.equal(item.triage_proposal.destination, 'unknown', `${c.case_id}: current A2 destination must remain unknown`);
      assert.ok(['inference', 'unknown'].includes(item.triage_proposal.label));
      if (item.source_span) {
        const { start, end } = item.source_span;
        assert.ok(Number.isInteger(start) && Number.isInteger(end) && start >= 0 && end > start);
        assert.equal(c.source_message.text.slice(start, end), item.text, `${c.case_id}/${item.item_id}: span must identify exact item text`);
      }
      assert.ok(['pending_human_decision', 'requires_human_assignment'].includes(item.auditor_proposal.status));
    }
  }
});

test('required edge-case families and controls are present', () => {
  const keys = data.cases.map((c) => c.scenario_key);
  for (const key of ['benign-quoted-instructions-1', 'indirect-kb-injection', 'indirect-attachment-injection-1', 'stale-source-1', 'conflicting-source-1', 'ambiguous-severity-1', 'severity-1-major-outage-1', 'clinical-advice-1', 'tool-outage-1', 'model-outage-1', 'privacy-marker-1', 'role-denial-1', 'missing-detail-pressure-1', 'multi-linked-1']) {
    assert.ok(keys.includes(key), `missing required scenario family ${key}`);
  }
  assert.ok(data.cases.some((c) => c.items.some((i) => i.triage_proposal.category === 'unknown')),
    'unknown category must remain represented for human Auditor assignment');
  for (const [gate, count] of Object.entries(data.coverage.gate_counts)) {
    assert.ok(count.challenge > 0, `${gate} needs positive/challenge examples`);
    assert.ok(count.control > 0, `${gate} needs negative/control examples`);
    assert.equal(count.cases.length, count.challenge + count.control);
  }
});

test('case proposals use approved bands and truthful parent-span reconstruction flags', () => {
  const allowedBands = new Set(['low', 'medium', 'high', 'unknown']);
  for (const c of data.cases) {
    assert.ok(allowedBands.has(c.auditor_decision_proposal.band),
      `${c.case_id}: urgent is a High/P1 attention flag, not a fourth band`);
    for (const item of c.items) {
      if (item.auditor_proposal?.band) {
        assert.ok(allowedBands.has(item.auditor_proposal.band),
          `${c.case_id}/${item.item_id}: invalid proposed band`);
      }
    }
    const items = [...c.items].sort((a, b) => a.source_span.start - b.source_span.start);
    let cursor = 0;
    let reconstructsParent = true;
    for (const item of items) {
      const { start, end } = item.source_span;
      if (start !== cursor || c.source_message.text.slice(start, end) !== item.text) {
        reconstructsParent = false;
      }
      cursor = end;
    }
    if (cursor !== c.source_message.text.length) reconstructsParent = false;
    assert.equal(c.segmentation.all_spans_reconstruct_parent, reconstructsParent,
      `${c.case_id}: reconstruction flag must reflect exact ordered spans`);
  }
});

test('proposed category vocabulary exists in the 80-row development catalog without importing its rows as labels', () => {
  const catalog = fs.readFileSync(catalogPath, 'utf8');
  const categories = new Set(data.cases.flatMap((c) => c.items.map((i) => i.triage_proposal.category)).filter((v) => v && v !== 'unknown'));
  for (const category of categories) assert.ok(catalog.includes(category), `category absent from support vocabulary: ${category}`);
  assert.equal(data.scope.development_catalog_is_not_evaluation_truth, true);
});

test('draft ticket text does not exactly duplicate current case suites or catalog text', () => {
  const existing = new Set();
  for (const dir of ['synthetic_data/cases', 'synthetic_data/item_cases', 'synthetic_data/manny_triage_cases']) {
    for (const file of walk(path.join(repo, dir))) {
      if (!file.endsWith('.json')) continue;
      try { for (const text of collectLongStrings(JSON.parse(fs.readFileSync(file, 'utf8')))) existing.add(normalize(text)); }
      catch { /* non-JSON fixture files are outside this exact duplicate check */ }
    }
  }
  const catalogText = normalize(fs.readFileSync(catalogPath, 'utf8'));
  for (const c of data.cases) {
    const text = normalize(c.source_message.text);
    assert.ok(!existing.has(text), `case duplicates an existing suite input: ${c.case_id}`);
    assert.ok(!catalogText.includes(text), `case duplicates catalog text: ${c.case_id}`);
  }
});
