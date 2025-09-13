(function(){
  const lb = document.getElementById('lightbox') || (() => {
    const d = document.createElement('div');
    d.id = 'lightbox';
    d.setAttribute('aria-hidden','true');
    d.style.display = 'none';
    d.style.position = 'fixed';
    d.style.inset = '0';
    d.style.background = 'rgba(0,0,0,.92)';
    d.style.zIndex = '9999';
    d.style.display = 'none';
    d.style.alignItems = 'center';
    d.style.justifyContent = 'center';
    d.style.padding = '2vh';
    d.innerHTML = `
      <button class="nav left" aria-label="Previous" style="position:fixed;left:12px;top:50%;transform:translateY(-50%);background:#1b1c1e;border:1px solid #4b4f56;color:#eee;border-radius:8px;padding:8px 10px;cursor:pointer">‹</button>
      <img src="" alt="enlarged" style="max-width:90vw;max-height:85vh;border-radius:10px;box-shadow:0 0 20px #000">
      <button class="nav right" aria-label="Next" style="position:fixed;right:12px;top:50%;transform:translateY(-50%);background:#1b1c1e;border:1px solid #4b4f56;color:#eee;border-radius:8px;padding:8px 10px;cursor:pointer">›</button>
      <button class="close" id="closeBtn" aria-label="Close" style="position:fixed;top:14px;right:14px;background:#1b1c1e;border:1px solid #4b4f56;color:#eee;border-radius:8px;padding:6px 10px;cursor:pointer">×</button>
    `;
    document.body.appendChild(d);
    return d;
  })();

  const im  = lb.querySelector('img');
  const btn = lb.querySelector('#closeBtn');
  const btnPrev = lb.querySelector('.nav.left');
  const btnNext = lb.querySelector('.nav.right');

  function imageList(){
    return Array.from(document.querySelectorAll('.tile img, figure img'));
  }
  function currentIndex(){
    const imgs = imageList();
    const idx  = imgs.findIndex(x => x.src === im.src);
    return { imgs, idx };
  }

  if (!window.openLB) {
    window.openLB = function(src, alt){
      lb.style.display = 'flex';
      im.src = src; im.alt = alt || '';
      document.body.classList.add('lb-open');
    };
  }
  if (!window.closeLB) {
    window.closeLB = function(){
      lb.style.display = 'none';
      im.src = '';
      document.body.classList.remove('lb-open');
    };
  }

  // click to open from tiles/figures
  document.querySelectorAll('.tile img, figure img').forEach(el=>{
    el.addEventListener('click',()=>openLB(el.src, el.alt));
  });

  // overlay interactions
  lb.addEventListener('click', e => { if (e.target === lb) closeLB(); });
  if (btn) btn.addEventListener('click', closeLB);

  // nav buttons
  function goNext(){ const {imgs, idx} = currentIndex(); if (idx > -1 && idx < imgs.length-1) openLB(imgs[idx+1].src, imgs[idx+1].alt); }
  function goPrev(){ const {imgs, idx} = currentIndex(); if (idx > 0) openLB(imgs[idx-1].src, imgs[idx-1].alt); }
  if (btnNext) btnNext.addEventListener('click', e => { e.stopImmediatePropagation(); goNext(); });
  if (btnPrev) btnPrev.addEventListener('click', e => { e.stopImmediatePropagation(); goPrev(); });

  // keyboard handler (capture, single action per press)
  window.addEventListener('keydown', (e) => {
    const isOpen = lb.style.display === 'flex';
    const key = e.key || e.code;

    // Normalize keys (some browsers report "Right"/"Left" instead of "ArrowRight"/"ArrowLeft")
    const isRight = key === 'ArrowRight' || key === 'Right';
    const isLeft  = key === 'ArrowLeft'  || key === 'Left';
    const isEsc   = key === 'Escape'     || key === 'Esc';

    if (isOpen) {
      if (isEsc) { e.preventDefault(); e.stopImmediatePropagation(); closeLB(); return; }
      if (isRight){ e.preventDefault(); e.stopImmediatePropagation(); goNext(); return; }
      if (isLeft){  e.preventDefault(); e.stopImmediatePropagation(); goPrev(); return; }
    } else if (isEsc) {
      // only when not open
      history.back();
      return;
    }
  }, true);
})();
