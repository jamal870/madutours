(function () {
  'use strict';
  // Mobile-Navigation
  var toggle = document.getElementById('navToggle'), nav = document.getElementById('nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && nav.classList.contains('open')) toggle.click(); });
  }
  // Video: Poster → iframe erst nach Klick (Datenschutz + Ladezeit)
  document.querySelectorAll('.video[data-video]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var f = document.createElement('iframe');
      f.src = btn.getAttribute('data-video');
      f.allow = 'autoplay; fullscreen; picture-in-picture';
      f.setAttribute('allowfullscreen', '');
      f.title = btn.getAttribute('aria-label') || 'Video';
      btn.innerHTML = '';
      btn.appendChild(f);
      btn.style.cursor = 'default';
    }, { once: true });
  });
  // Lightbox
  var lb = document.getElementById('lightbox');
  if (lb) {
    var items = Array.prototype.slice.call(document.querySelectorAll('[data-lightbox]')), idx = 0;
    var img = lb.querySelector('img');
    function show(i) { idx = (i + items.length) % items.length; img.src = items[idx].getAttribute('href'); lb.hidden = false; document.body.style.overflow = 'hidden'; }
    function hide() { lb.hidden = true; img.removeAttribute('src'); document.body.style.overflow = ''; }
    items.forEach(function (a, i) { a.addEventListener('click', function (e) { e.preventDefault(); show(i); }); });
    lb.querySelector('.lb-close').addEventListener('click', hide);
    lb.querySelector('.lb-prev').addEventListener('click', function () { show(idx - 1); });
    lb.querySelector('.lb-next').addEventListener('click', function () { show(idx + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) hide(); });
    document.addEventListener('keydown', function (e) {
      if (lb.hidden) return;
      if (e.key === 'Escape') hide(); else if (e.key === 'ArrowLeft') show(idx - 1); else if (e.key === 'ArrowRight') show(idx + 1);
    });
    var tx = 0;
    lb.addEventListener('touchstart', function (e) { tx = e.changedTouches[0].clientX; }, { passive: true });
    lb.addEventListener('touchend', function (e) { var d = e.changedTouches[0].clientX - tx; if (Math.abs(d) > 50) show(d < 0 ? idx + 1 : idx - 1); }, { passive: true });
  }
  // Formular: speichert jede Anfrage in Netlify Forms; optional zusätzlich WhatsApp mit vorformuliertem Text
  var form = document.getElementById('bookingForm');
  if (form) {
    var via = 'form';
    var buttons = form.querySelectorAll('button[type=submit]');
    buttons.forEach(function (b) { b.addEventListener('click', function () { via = b.getAttribute('data-via'); }); });
    var err = document.getElementById('formError'), ok = document.getElementById('formOk');
    function val(id) { var el = document.getElementById(id); return el ? el.value.trim() : ''; }
    function label(id) { var l = document.getElementById(id).closest('label'); return l ? l.querySelector('span').textContent.replace(' *', '') : id; }
    function waText() {
      var lines = [form.getAttribute('data-subject') + ' – Madutours', ''];
      ['f-name', 'f-email', 'f-phone', 'f-people', 'f-arrival', 'f-departure', 'f-type'].forEach(function (id) { if (val(id)) lines.push(label(id) + ': ' + val(id)); });
      lines.push('', val('f-message'));
      return lines.join('\n');
    }
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      err.hidden = true; ok.hidden = true;
      if (!val('f-name') || !val('f-message')) { err.textContent = form.getAttribute('data-required'); err.hidden = false; return; }
      var useWa = via === 'wa';
      // WhatsApp-Fenster sofort öffnen, damit der Popup-Blocker nicht eingreift
      if (useWa) window.open('https://wa.me/' + form.getAttribute('data-wa') + '?text=' + encodeURIComponent(waText()), '_blank', 'noopener');
      var original = [];
      buttons.forEach(function (b) { b.disabled = true; original.push(b.innerHTML); });
      var body = new URLSearchParams(new FormData(form)).toString();
      fetch('/', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: body })
        .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); ok.textContent = form.getAttribute('data-ok'); ok.hidden = false; form.reset(); })
        .catch(function () { if (!useWa) { err.textContent = form.getAttribute('data-fail'); err.hidden = false; } })
        .then(function () { buttons.forEach(function (b, i) { b.disabled = false; b.innerHTML = original[i]; }); });
    });
  }
})();
