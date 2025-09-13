(function(){
  // Ensure we have a lightbox and helpers; if your page already defines them, we reuse.
  const lb = document.getElementById('lightbox') || (function(){
    const d = document.createElement('div');
    d.id = 'lightbox';
    d.setAttribute('aria-hidden','true');
    d.style.display = 'none';
    d.innerHTML = '<img src="" alt="enlarged"><button class="close" id="closeBtn">× Close</button>';
    document.body.appendChild(d);
    return d;
  })();
  const im = lb.querySelector('img');
  const btn = document.getElementById('closeBtn') || lb.querySelector('#closeBtn');

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

  // Click to open
  document.querySelectorAll('.tile img, figure img').forEach(el=>{
    el.addEventListener('click',()=>openLB(el.src, el.alt));
  });

  // Click outside or on button closes
  lb.addEventListener('click',e=>{ if(e.target===lb) closeLB(); });
  if (btn) btn.addEventListener('click', closeLB);

  // Keyboard: Esc closes (or goes back), →/← navigate when open
  window.addEventListener('keydown', (e)=>{
    const isOpen = lb.style.display === 'flex';
    const imgs = Array.from(document.querySelectorAll('.tile img, figure img'));
    const idx = imgs.findIndex(x => x.src === im.src);

    if (e.key === 'Escape') {
      if (isOpen) {
        e.preventDefault(); e.stopImmediatePropagation();
        closeLB();  // close only, do NOT history.back()
      } else {
        // lightbox not open -> go back once
        history.back();
      }
    }

    if (isOpen && e.key === 'ArrowRight' && idx > -1 && idx < imgs.length - 1) {
      e.preventDefault(); e.stopImmediatePropagation();
      openLB(imgs[idx+1].src, imgs[idx+1].alt);
    }
    if (isOpen && e.key === 'ArrowLeft' && idx > 0) {
      e.preventDefault(); e.stopImmediatePropagation();
      openLB(imgs[idx-1].src, imgs[idx-1].alt);
    }
  }, true);
})();
