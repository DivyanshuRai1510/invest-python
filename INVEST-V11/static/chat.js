(function () {
  const box = document.getElementById('chat');
  if (!box) return;
  const uid = box.dataset.uid;
  let last = parseInt(box.dataset.last || '0', 10);
  const latest = document.getElementById('latest');
  const textarea = document.getElementById('body');

  function scrollDown() { latest.scrollIntoView({ block: 'end' }); }

  function addBubble(m) {
    const row = document.createElement('div');
    row.className = 'chat-row' + (m.mine ? ' mine' : '');
    row.dataset.id = m.id;
    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble';
    const text = document.createElement('div');
    text.className = 'message-body';
    text.textContent = m.body;
    bubble.append(text);
    (m.attachments || []).forEach((a) => {
      const card = document.createElement('div');
      card.className = 'message-attachment';
      if ((a.mime_type || '').startsWith('image/')) {
        const link = document.createElement('a');
        link.href = a.inline_url;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        const img = document.createElement('img');
        img.src = a.inline_url || a.url;
        img.alt = a.name;
        img.loading = 'lazy';
        img.onerror = () => { img.remove(); link.classList.add('image-unavailable'); link.textContent = 'Preview unavailable'; };
        link.append(img);
        card.append(link);
      } else {
        const icon = document.createElement('span');
        icon.textContent = '📄';
        icon.style.fontSize = '24px';
        card.append(icon);
      }
      const details = document.createElement('div');
      const name = document.createElement('div');
      name.textContent = a.name;
      const link = document.createElement('a');
      link.href = a.url;
      link.download = a.name;
      link.textContent = 'Download file';
      details.append(name, link);
      card.append(details);
      bubble.append(card);
    });
    if (window.investEnrichMessages) window.investEnrichMessages(bubble);
    const stamp = document.createElement('div');
    stamp.className = 'chat-stamp';
    stamp.textContent = (m.mine ? 'You' : 'Message') + ' · ' + m.time;
    row.append(bubble, stamp);
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
