/* Shared helpers for the worksheet site. */

const LETTERS = ['A', 'B', 'C', 'D'];

/* Resolve paths relative to the site root so this works both at
   username.github.io/repo/ and on a plain local server. */
function sitePath(rel) {
  const base = window.location.pathname.replace(/[^/]*$/, '');
  return base + rel;
}

async function getJSON(rel) {
  const res = await fetch(sitePath(rel), { cache: 'no-cache' });
  if (!res.ok) throw new Error('Could not load ' + rel + ' (HTTP ' + res.status + ')');
  return res.json();
}

async function loadManifest() {
  return getJSON('data/index.json');
}

async function loadWorksheet(entryOrFile) {
  const file = typeof entryOrFile === 'string' ? entryOrFile : entryOrFile.file;
  return getJSON(file);
}

/* Rebuild the fixed display order of a question's choices.
   order is a 4-item array of tokens: "c" = correct, "dN" = distractors[N]. */
function displayChoices(q) {
  return q.order.map(function (tok) {
    if (tok === 'c') return q.correct;
    return q.distractors[parseInt(tok.slice(1), 10)];
  });
}

/* The letter (A-D) of the correct answer, derived from order.
   Falls back to the stored correctLetter if present. */
function correctLetter(q) {
  const idx = q.order.indexOf('c');
  return idx >= 0 ? LETTERS[idx] : (q.correctLetter || '?');
}

function answerKeyString(worksheet) {
  return worksheet.questions.map(correctLetter).join('');
}

/* Flatten the manifest into one searchable list. */
function allWorksheets(manifest) {
  const out = [];
  manifest.sets.forEach(function (set) {
    set.worksheets.forEach(function (w) {
      out.push(Object.assign({}, w, { setId: set.id, setTitle: set.title }));
    });
  });
  return out;
}

function escapeHTML(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function showLoadError(container, err) {
  container.innerHTML =
    '<div class="error"><strong>Could not load worksheet data.</strong><br>' +
    escapeHTML(err.message) +
    '<br><br>If you opened this file directly from your computer (a <code>file://</code> address), ' +
    'browsers block loading the JSON files. Use the published GitHub Pages link instead, ' +
    'or run <code>python3 -m http.server</code> inside the repo folder and open ' +
    '<code>http://localhost:8000</code>.</div>';
}
