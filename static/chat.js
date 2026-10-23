(function () {
  const box = document.getElementById('chat');
  if (!box) return;
  const uid = box.dataset.uid;
  let last = parseInt(box.dataset.last || '0', 10);
  const latest = document.getElementById('latest');
  const empty = document.getElementById('empty-note');
  const textarea = document.getElementById('body');

  function scrollDown() { latest.scrollIntoView({ block: 'end' }); }

  function addBubble(m) {
    if (empty) empty.remove();
    const row = document.createElement('div');
    row.className = 'flex ' + (m.mine ? 'justify-end' : 'justify-start');
    row.dataset.id = m.id;
    const bubble = document.createElement('div');
    bubble.className = 'max-w-[75%] rounded-2xl px-4 py-2.5 text-sm ' +
      (m.mine ? 'bg-brand-blue text-white rounded-br-sm' : 'bg-white border border-slate-200 rounded-bl-sm');
    const text = document.createElement('p');
    text.className = 'whitespace-pre-line';
    text.textContent = m.body;
    const time = document.createElement('p');
    time.className = 'text-[10px] mt-1 ' + (m.mine ? 'text-blue-100' : 'text-slate-400');
    time.textContent = m.time;
    bubble.append(text, time);
    row.append(bubble);
    box.insertBefore(row, latest);
    last = Math.max(last, m.id);
  }

  async function poll() {
    try {
      const res = await fetch(`/messages/${uid}/poll?after=${last}`, { credentials: 'same-origin' });
      if (!res.ok) return;
      const items = await res.json();
      if (items.length) { items.forEach(addBubble); scrollDown(); }
    } catch (e) { /* network hiccup: try again on the next tick */ }
  }

  // Enter sends, Shift+Enter adds a new line
  textarea.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      textarea.form.requestSubmit();
    }
  });

  scrollDown();
  setInterval(poll, 4000);
})();
