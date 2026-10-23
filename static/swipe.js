(function () {
  const stack = document.getElementById('stack');
  if (!stack) return;

  const emptyEl = document.getElementById('empty');
  const remainingEl = document.getElementById('remaining');
  const interestedEl = document.getElementById('count-interested');
  const history = [];          // swipes made on this page, newest last
  let drag = null;

  const topCard = () => stack.querySelector('.swipe-card:not(.gone)');

  function refreshCounts() {
    const left = stack.querySelectorAll('.swipe-card:not(.gone)').length;
    remainingEl.textContent = left;
    emptyEl.classList.toggle('hidden', left > 0);
  }

  function bump(el, delta) {
    el.textContent = Math.max(0, parseInt(el.textContent, 10) + delta);
  }

  async function post(url, body) {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify(body || {}),
    });
    if (res.status === 401) {
      window.location.href = '/login?next=/swipe/';
      throw new Error('login required');
    }
    if (!res.ok) throw new Error('Request failed: ' + res.status);
    return res.json();
  }

  function flyOut(card, dir) {
    card.classList.add('gone');
    card.style.transform = `translateX(${dir * 900}px) rotate(${dir * 25}deg)`;
    card.style.opacity = '0';
    setTimeout(() => { card.style.display = 'none'; }, 260);
  }

  async function decide(action) {
    const card = topCard();
    if (!card) return;
    try {
      await post('/swipe/act', { company_id: Number(card.dataset.id), action: action });
    } catch (err) {
      if (err.message !== 'login required') alert('Could not save your swipe. Please try again.');
      resetCard(card);
      return;
    }
    history.push({ card: card, action: action });
    const dir = action === 'passed' ? -1 : (action === 'interested' ? 1 : 0);
    flyOut(card, dir);
    if (action === 'interested') bump(interestedEl, 1);
    refreshCounts();
  }

  function resetCard(card) {
    card.style.transition = 'transform .25s ease';
    card.style.transform = '';
    card.querySelectorAll('.stamp').forEach((s) => (s.style.opacity = 0));
  }

  async function undo() {
    const last = history.pop();
    if (!last) return;
    try {
      await post('/swipe/undo', {});
    } catch (err) {
      history.push(last);
      if (err.message !== 'login required') alert('Could not undo. Please try again.');
      return;
    }
    const card = last.card;
    card.classList.remove('gone');
    card.style.display = '';
    card.style.transition = 'transform .3s ease, opacity .3s ease';
    card.style.transform = '';
    card.style.opacity = '1';
    if (last.action === 'interested') bump(interestedEl, -1);
    refreshCounts();
  }

  // Drag / swipe with mouse, touch or pen
  stack.addEventListener('pointerdown', (e) => {
    const card = e.target.closest('.swipe-card');
    if (!card || card !== topCard()) return;
    drag = { card: card, x0: e.clientX, dx: 0, moved: false };
    card.setPointerCapture(e.pointerId);
    card.style.transition = 'none';
  });

  stack.addEventListener('pointermove', (e) => {
    if (!drag) return;
    drag.dx = e.clientX - drag.x0;
    if (Math.abs(drag.dx) > 6) drag.moved = true;
    drag.card.style.transform = `translateX(${drag.dx}px) rotate(${drag.dx / 18}deg)`;
    drag.card.querySelector('.stamp.like').style.opacity = Math.min(1, Math.max(0, drag.dx / 120));
    drag.card.querySelector('.stamp.nope').style.opacity = Math.min(1, Math.max(0, -drag.dx / 120));
  });

  function endDrag() {
    if (!drag) return;
    const { card, dx, moved } = drag;
    drag = null;
    if (moved) card.dataset.dragged = '1';
    if (dx > 110) decide('interested');
    else if (dx < -110) decide('passed');
    else resetCard(card);
  }
  stack.addEventListener('pointerup', endDrag);
  stack.addEventListener('pointercancel', endDrag);

  // A tap (not a drag) opens the company page
  stack.addEventListener('click', (e) => {
    const card = e.target.closest('.swipe-card');
    if (!card) return;
    if (card.dataset.dragged === '1') { card.dataset.dragged = ''; return; }
    window.location.href = card.dataset.url;
  });

  document.getElementById('btn-pass').addEventListener('click', () => decide('passed'));
  document.getElementById('btn-like').addEventListener('click', () => decide('interested'));
  document.getElementById('btn-save').addEventListener('click', () => decide('saved'));
  document.getElementById('btn-undo').addEventListener('click', undo);

  document.addEventListener('keydown', (e) => {
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) return;
    if (e.key === 'ArrowLeft') decide('passed');
    else if (e.key === 'ArrowRight') decide('interested');
    else if (e.key === 'ArrowUp') decide('saved');
    else if (e.key === 'Backspace') { e.preventDefault(); undo(); }
  });

  refreshCounts();
})();
