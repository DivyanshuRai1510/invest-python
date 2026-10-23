(function() {
  const stack = document.getElementById('cardStack');
  const btnPass = document.getElementById('btnPass');
  const btnSave = document.getElementById('btnSave');
  const btnLike = document.getElementById('btnLike');
  const btnUndo = document.getElementById('btnUndo');
  const interestList = document.getElementById('interestList');

  let currentIndex = 0;
  const cards = Array.from(stack.querySelectorAll('.card-item'));
  let dragOffset = { x: 0, y: 0 };
  let startX = 0, startY = 0;

  if (cards.length === 0) return;

  function updateCardPositions() {
    cards.forEach((card, idx) => {
      const offset = Math.max(0, idx - currentIndex);
      card.style.zIndex = 100 - offset;
      card.style.transform = offset === 0 ? 'scale(1) translateY(0)' : `scale(${1 - offset * 0.05}) translateY(${offset * 10}px)`;
      card.style.pointerEvents = offset === 0 ? 'auto' : 'none';
      card.style.opacity = offset === 0 ? '1' : '0';
    });
  }

  function action(kind) {
    if (currentIndex >= cards.length) return;
    const card = cards[currentIndex];
    const cid = parseInt(card.dataset.companyId);
    const name = card.querySelector('.card-title').textContent;

    fetch('/swipe/act', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company_id: cid, action: kind })
    }).then(r => r.json()).then(data => {
      if (data.ok) {
        if (kind === 'interested') {
          const li = document.createElement('li');
          li.className = 'py-2 text-slate-700 truncate';
          li.textContent = name;
          interestList.insertBefore(li, interestList.firstChild);
          if (interestList.children.length > 5) interestList.lastChild.remove();
        }
        flyOut(card, kind);
      }
    });
  }

  function flyOut(card, kind) {
    const stamp = card.querySelector(kind === 'interested' ? '.stamp.like' : kind === 'saved' ? '.stamp' : '.stamp.nope');
    if (stamp) stamp.style.opacity = '1';
    
    const deg = kind === 'interested' ? 20 : kind === 'saved' ? 0 : -20;
    const tx = kind === 'interested' ? 500 : kind === 'saved' ? 0 : -500;
    card.classList.add('flyOut');
    card.style.transform = `translate(${tx}px, -500px) rotate(${deg}deg)`;
    
    setTimeout(() => {
      currentIndex++;
      updateCardPositions();
      card.classList.remove('flyOut');
      card.style.transform = '';
      stamp.style.opacity = '0';
      if (currentIndex >= cards.length && interestList.parentElement) {
        interestList.parentElement.innerHTML = '<p class="text-center text-sm text-slate-500">All reviewed!</p>';
      }
    }, 600);
  }

  function startDrag(e) {
    if (currentIndex >= cards.length) return;
    const card = cards[currentIndex];
    startX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
    startY = e.type.includes('touch') ? e.touches[0].clientY : e.clientY;
    dragOffset = { x: 0, y: 0 };
    card.dataset.dragged = 'false';
    document.addEventListener(e.type.includes('touch') ? 'touchmove' : 'mousemove', drag);
    document.addEventListener(e.type.includes('touch') ? 'touchend' : 'mouseup', endDrag);
  }

  function drag(e) {
    const card = cards[currentIndex];
    const clientX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
    const clientY = e.type.includes('touch') ? e.touches[0].clientY : e.clientY;
    dragOffset.x = clientX - startX;
    dragOffset.y = clientY - startY;
    const deg = dragOffset.x * 0.1;
    card.style.transform = `translate(${dragOffset.x}px, ${dragOffset.y}px) rotate(${deg}deg)`;
    if (Math.abs(dragOffset.x) > 10) card.dataset.dragged = 'true';
  }

  function endDrag(e) {
    document.removeEventListener(e.type.includes('touch') ? 'touchmove' : 'mousemove', drag);
    document.removeEventListener(e.type.includes('touch') ? 'touchend' : 'mouseup', endDrag);
    if (currentIndex >= cards.length) return;

    const card = cards[currentIndex];
    const threshold = 120;
    if (dragOffset.x > threshold) action('interested');
    else if (dragOffset.x < -threshold) action('passed');
    else if (dragOffset.y > threshold) action('saved');
    else {
      card.style.transform = '';
      card.dataset.dragged = 'false';
    }
  }

  btnPass.addEventListener('click', () => action('passed'));
  btnSave.addEventListener('click', () => action('saved'));
  btnLike.addEventListener('click', () => action('interested'));
  btnUndo.addEventListener('click', () => {
    fetch('/swipe/undo', { method: 'POST' }).then(r => r.json()).then(data => {
      if (data.ok && currentIndex > 0) {
        currentIndex--;
        updateCardPositions();
      }
    });
  });

  const pointerStart = e => { if (e.button === 0 || !('button' in e)) startDrag(e); };
  stack.addEventListener('pointerdown', pointerStart);
  stack.addEventListener('touchstart', startDrag);

  document.addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft') action('passed');
    else if (e.key === 'ArrowRight') action('interested');
    else if (e.key === 'ArrowDown') action('saved');
    else if (e.key === 'Backspace') {
      e.preventDefault();
      btnUndo.click();
    }
  });

  updateCardPositions();
})();
