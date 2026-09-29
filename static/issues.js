/* Sayı ve jenerik: issue documents, article order, front matter and numbered outputs. */
window.issueWorkspace = (() => {
  const byId = id => document.getElementById(id);
  let issues = [], current = null, articles = [], timer = null, saving = null, dirty = false;
  const json = async (url, options = {}) => {
    const response = await aiditorFetch(url, {...options, headers: {'Content-Type': 'application/json', ...(options.headers || {})}});
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.error || 'İşlem tamamlanamadı.');
    return result;
  };
  const status = (text, state = 'saved') => { const el = byId('issue-save-status'); el.textContent = text; el.dataset.state = state; };
  const fields = () => document.querySelectorAll('[data-issue-field]');

  async function refreshList(selectId) {
    const result = await json('/api/issues');
    issues = result.issues;
    const select = byId('issue-select'); select.replaceChildren();
    for (const item of issues) { const option = document.createElement('option'); option.value = item.id; option.textContent = item.title; select.append(option); }
    const id = selectId || (issues[0] && issues[0].id);
    if (id) { select.value = id; await open(id); } else { current = null; byId('issue-form').hidden = true; byId('issue-outputs').hidden = true; byId('issue-delete').disabled = true; }
  }

  async function open(id) {
    const result = await json('/api/issues/' + id);
    current = {id, revision: result.issue.revision, data: result.issue.data};
    articles = (await json('/api/articles')).articles;
    render();
  }

  function render() {
    byId('issue-form').hidden = false; byId('issue-outputs').hidden = false; byId('issue-delete').disabled = false;
    fields().forEach(input => { input.value = current.data[input.dataset.issueField] ?? ''; });
    const list = byId('issue-articles'); list.replaceChildren();
    const chosen = current.data.articles.map(item => item.id);
    const known = new Map(articles.map(item => [item.id, item]));
    const rows = [...chosen.filter(id => known.has(id)), ...articles.map(item => item.id).filter(id => !chosen.includes(id))];
    rows.forEach((id, index) => {
      const item = known.get(id), selected = chosen.includes(id);
      const row = document.createElement('div'); row.className = 'd-flex align-items-center gap-2 mb-1';
      const box = document.createElement('input'); box.type = 'checkbox'; box.className = 'form-check-input'; box.checked = selected;
      box.setAttribute('aria-label', item.title + ' sayıya eklensin');
      box.addEventListener('change', () => { toggle(id, box.checked); });
      const label = document.createElement('span'); label.textContent = item.title + (item.authors ? ' · ' + item.authors : '');
      row.append(box, label);
      if (selected) {
        const position = chosen.indexOf(id);
        for (const [text, delta, name] of [['↑', -1, 'yukarı'], ['↓', 1, 'aşağı']]) {
          const button = document.createElement('button'); button.type = 'button'; button.className = 'btn btn-sm btn-outline-secondary';
          button.textContent = text; button.setAttribute('aria-label', item.title + ' ' + name + ' taşı');
          button.disabled = position + delta < 0 || position + delta >= chosen.length;
          button.addEventListener('click', () => move(id, delta)); row.append(button);
        }
      }
      list.append(row);
    });
    if (!rows.length) list.textContent = 'Henüz kayıtlı makale yok. Makaleler sekmesinde bir makale kaydedin.';
  }

  function toggle(id, on) {
    const list = current.data.articles.filter(item => item.id !== id);
    if (on) list.push({id});
    current.data.articles = list; changed(); render();
  }
  function move(id, delta) {
    const list = current.data.articles, index = list.findIndex(item => item.id === id), target = index + delta;
    if (index < 0 || target < 0 || target >= list.length) return;
    [list[index], list[target]] = [list[target], list[index]]; changed(); render();
  }
  function changed() { dirty = true; status('Kaydediliyor…', 'pending'); clearTimeout(timer); timer = setTimeout(flush, 600); }

  async function flush() {
    if (!current || saving) { if (saving) await saving; if (!dirty) return true; }
    clearTimeout(timer);
    fields().forEach(input => { current.data[input.dataset.issueField] = input.value; });
    dirty = false;
    saving = (async () => {
      try {
        const result = await json('/api/issues/' + current.id, {method: 'PUT', body: JSON.stringify({data: current.data, base_revision: current.revision})});
        current.revision = result.issue.revision;
        const entry = issues.find(item => item.id === current.id); if (entry) { entry.title = result.issue.title; }
        const option = [...byId('issue-select').options].find(o => o.value === current.id); if (option) option.textContent = result.issue.title;
        status('Sayı kaydedildi'); return true;
      } catch (error) { dirty = true; status('Kaydedilemedi: ' + error.message, 'error'); return false; }
      finally { saving = null; }
    })();
    return saving;
  }

  async function build(kind) {
    const buttons = document.querySelectorAll('[data-issue-build]'); const out = byId('issue-build-status');
    if (!await flush() && dirty) { out.textContent = 'Önce sayı kaydı tamamlanmalıdır.'; return; }
    buttons.forEach(b => { b.disabled = true; });
    out.textContent = 'Hazırlanıyor…';
    try {
      const result = await json('/api/issues/' + current.id + '/build', {method: 'POST', body: JSON.stringify({kind})});
      const body = byId('issue-ranges').querySelector('tbody'); body.replaceChildren();
      for (const range of result.ranges || []) {
        const row = body.insertRow(); row.insertCell().textContent = range.title;
        row.insertCell().textContent = range.start === range.end ? String(range.start) : range.start + '–' + range.end;
      }
      byId('issue-ranges').hidden = !(result.ranges || []).length;
      if (result.key) {
        await saveOutputFile('/download_file/' + result.key, result.filename, 'application/zip', out);
      } else out.textContent = 'Sayfa aralıkları hesaplandı.';
    } catch (error) { out.textContent = 'Hata: ' + error.message; }
    finally { buttons.forEach(b => { b.disabled = false; }); }
  }

  function init() {
    byId('issue-new').addEventListener('click', async () => {
      const id = crypto.randomUUID();
      try {
        await json('/api/issues/' + id, {method: 'PUT', body: JSON.stringify({data: {first_page: '1', articles: []}, base_revision: 0})});
        await refreshList(id);
      } catch (error) { status('Sayı oluşturulamadı: ' + error.message, 'error'); }
    });
    byId('issue-delete').addEventListener('click', async () => {
      if (!current || !confirm('Bu sayı silinsin mi? Makaleler silinmez.')) return;
      try { await json('/api/issues/' + current.id, {method: 'DELETE', body: JSON.stringify({base_revision: current.revision})}); await refreshList(); }
      catch (error) { status('Silinemedi: ' + error.message, 'error'); }
    });
    byId('issue-select').addEventListener('change', async event => { await flush(); await open(event.target.value); });
    byId('issue-form').addEventListener('input', event => { if (!current) return; const key = event.target.dataset?.issueField; if (key) current.data[key] = event.target.value; changed(); });
    byId('issue-form').addEventListener('submit', event => event.preventDefault());
    document.querySelectorAll('[data-issue-build]').forEach(button => button.addEventListener('click', () => build(button.dataset.issueBuild)));
    byId('issues-tab').addEventListener('click', () => refreshList(current && current.id).catch(error => status(error.message, 'error')));
  }
  document.addEventListener('DOMContentLoaded', init);
  return {flush, get current() { return current; }};
})();
