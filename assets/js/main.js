/* ORITEC site behaviour. No dependencies. */
(() => {
  'use strict';

  const doc = document.documentElement;
  doc.classList.add('js');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));

  /* ---------- Header: scroll state, mobile menu, active link ---------- */
  const header = document.querySelector('[data-header]');
  const toggle = document.querySelector('[data-menu-toggle]');
  const menu = document.querySelector('[data-mobile-menu]');

  const setMenu = (open) => {
    toggle.setAttribute('aria-expanded', String(open));
    toggle.querySelector('.sr-only').textContent = open ? 'Close menu' : 'Open menu';
    menu.hidden = !open;
    header.classList.toggle('is-scrolled', open || window.scrollY > 24);
  };
  toggle.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
  menu.addEventListener('click', (e) => { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !menu.hidden) { setMenu(false); toggle.focus(); } });
  window.matchMedia('(min-width: 1181px)').addEventListener('change', (e) => { if (e.matches) setMenu(false); });

  const navLinks = [...document.querySelectorAll('.nav-links a')];
  const sections = navLinks.map((a) => document.querySelector(a.getAttribute('href'))).filter(Boolean);
  const spy = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (!en.isIntersecting) return;
      navLinks.forEach((a) => a.setAttribute('aria-current', String(a.getAttribute('href') === '#' + en.target.id)));
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  sections.forEach((s) => spy.observe(s));

  /* ---------- Reveal on view ---------- */
  const revealables = document.querySelectorAll('.reveal, .reveal-lines, [data-flow]');
  if (reduceMotion || !('IntersectionObserver' in window)) {
    revealables.forEach((el) => el.classList.add('is-in'));
  } else {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: .12 });
    revealables.forEach((el) => io.observe(el));
  }

  /* ---------- Counters ---------- */
  const counters = document.querySelectorAll('[data-count]');
  const runCounter = (el) => {
    const target = Number(el.dataset.count);
    const suffix = el.dataset.suffix || '';
    if (reduceMotion) { el.textContent = target + suffix; return; }
    const start = performance.now();
    const dur = 1600;
    const tick = (now) => {
      const t = clamp((now - start) / dur);
      const eased = 1 - Math.pow(1 - t, 4);
      el.textContent = Math.round(target * eased) + suffix;
      if (t < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };
  const countIO = new IntersectionObserver((entries) => {
    entries.forEach((en) => { if (en.isIntersecting) { runCounter(en.target); countIO.unobserve(en.target); } });
  }, { threshold: .6 });
  counters.forEach((el) => { el.textContent = '0' + (el.dataset.suffix || ''); countIO.observe(el); });

  /* ---------- Scroll-linked motion ---------- */
  const consoleEl = document.querySelector('.console');
  const stage = document.querySelector('[data-tilt]');
  const hs = document.querySelector('[data-hscroll]');
  const hsTrack = document.querySelector('[data-hs-track]');
  const steps = document.querySelector('[data-steps]');
  const stepItems = steps ? [...steps.children] : [];
  const tiles = [...document.querySelectorAll('.ftile')];
  const found = document.querySelector('[data-found]');
  const cta = document.querySelector('.cta');
  const hsQuery = window.matchMedia('(min-width: 861px)');

  // Progress of an element through the viewport: 0 when its top hits `from`, 1 when it reaches `to`.
  const progress = (el, from = 1, to = .3) => {
    const r = el.getBoundingClientRect();
    const vh = window.innerHeight;
    return clamp((vh * from - r.top) / (vh * (from - to)));
  };

  const sizeHorizontal = () => {
    if (!hs) return;
    if (!hsQuery.matches || reduceMotion) { hs.style.height = ''; hsTrack.style.transform = ''; return; }
    const extra = hsTrack.scrollWidth - window.innerWidth;
    hs.style.height = (window.innerHeight + Math.max(0, extra)) + 'px';
  };

  let ticking = false;
  const onScroll = () => {
    ticking = false;
    const y = window.scrollY;
    if (menu.hidden) header.classList.toggle('is-scrolled', y > 24);
    if (reduceMotion) return;

    if (stage) consoleEl.style.setProperty('--t', progress(stage, 1, .35).toFixed(3));

    if (hs && hsQuery.matches) {
      const r = hs.getBoundingClientRect();
      const total = hs.offsetHeight - window.innerHeight;
      const p = total > 0 ? clamp(-r.top / total) : 0;
      const extra = hsTrack.scrollWidth - window.innerWidth;
      hsTrack.style.transform = `translate3d(${(-extra * p).toFixed(1)}px,0,0)`;
    }

    if (steps) {
      const r = steps.getBoundingClientRect();
      const line = clamp((window.innerHeight * .6 - r.top) / r.height);
      steps.style.setProperty('--progress', line.toFixed(3));
      stepItems.forEach((li) => {
        li.classList.toggle('is-on', li.getBoundingClientRect().top < window.innerHeight * .6);
      });
    }

    if (found) {
      tiles.forEach((t, i) => {
        const p = progress(found, 1.05 - i * .03, .45);
        t.style.setProperty('--p', p.toFixed(3));
      });
    }

    if (cta) cta.style.setProperty('--p', progress(cta, 1, .2).toFixed(3));
  };
  const requestTick = () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } };
  window.addEventListener('scroll', requestTick, { passive: true });
  window.addEventListener('resize', () => { sizeHorizontal(); drawTraces(); requestTick(); });
  hsQuery.addEventListener('change', () => { sizeHorizontal(); requestTick(); });

  /* ---------- Services: traces from each node into the core ---------- */
  const flow = document.querySelector('[data-flow]');
  const traceSvg = document.querySelector('[data-traces]');
  const core = document.querySelector('[data-core]');
  const nodes = [...document.querySelectorAll('[data-node]')];
  const NS = 'http://www.w3.org/2000/svg';

  function drawTraces() {
    if (!flow || getComputedStyle(traceSvg).display === 'none') return;
    const box = flow.getBoundingClientRect();
    const c = core.querySelector('.core-chip').getBoundingClientRect();
    const cy = c.top + c.height / 2 - box.top;
    traceSvg.setAttribute('viewBox', `0 0 ${box.width} ${box.height}`);
    traceSvg.innerHTML = `<defs><linearGradient id="traceGrad" x1="0" x2="1"><stop offset="0" stop-color="#9DB8FF" stop-opacity="0"/><stop offset=".5" stop-color="#C9D8FF"/><stop offset="1" stop-color="#9DB8FF" stop-opacity="0"/></linearGradient></defs>`;
    nodes.forEach((n, i) => {
      const r = n.getBoundingClientRect();
      const left = r.left + r.width / 2 < c.left;
      const sx = (left ? r.right : r.left) - box.left;
      const sy = r.top + r.height / 2 - box.top;
      const ex = (left ? c.left : c.right) - box.left;
      const ey = cy + ((i % 4) - 1.5) * 14;
      const mx = sx + (ex - sx) * .55;
      const d = `M${sx} ${sy} H${mx} V${ey} H${ex}`;
      ['base', 'pulse'].forEach((cls) => {
        const p = document.createElementNS(NS, 'path');
        p.setAttribute('d', d);
        if (cls === 'pulse') { p.classList.add('pulse'); p.style.setProperty('--pd', (i * .37).toFixed(2) + 's'); }
        p.dataset.idx = i;
        traceSvg.appendChild(p);
      });
    });
  }
  nodes.forEach((n, i) => {
    const hot = (on) => {
      n.classList.toggle('is-hot', on);
      traceSvg.querySelectorAll(`path[data-idx="${i}"]:not(.pulse)`).forEach((p) => p.classList.toggle('is-hot', on));
    };
    n.addEventListener('mouseenter', () => hot(true));
    n.addEventListener('mouseleave', () => hot(false));
  });

  /* ---------- Projects: swap sticky image as items pass the centre ---------- */
  const projItems = [...document.querySelectorAll('[data-project]')];
  const projImgs = [...document.querySelectorAll('.proj-media img')];
  const projIO = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (!en.isIntersecting) return;
      const idx = projItems.indexOf(en.target);
      projItems.forEach((p, i) => p.classList.toggle('is-active', i === idx));
      projImgs.forEach((img, i) => img.classList.toggle('is-active', i === idx));
    });
  }, { rootMargin: '-45% 0px -45% 0px' });
  projItems.forEach((p) => projIO.observe(p));

  /* ---------- Contact form ---------- */
  const form = document.querySelector('[data-form]');
  const status = document.querySelector('[data-form-status]');
  document.querySelectorAll('[data-prefill]').forEach((a) => a.addEventListener('click', () => {
    form.elements.type.value = a.dataset.prefill;
  }));

  const showError = (field, msg) => {
    const wrap = field.closest('.field');
    wrap.classList.add('has-error');
    field.setAttribute('aria-invalid', 'true');
    let err = wrap.querySelector('.field-error');
    if (!err) {
      err = document.createElement('p');
      err.className = 'field-error';
      err.id = field.id + '-err';
      wrap.appendChild(err);
      field.setAttribute('aria-describedby', err.id);
    }
    err.textContent = msg;
  };
  const clearError = (field) => {
    const wrap = field.closest('.field');
    wrap.classList.remove('has-error');
    field.removeAttribute('aria-invalid');
    wrap.querySelector('.field-error')?.remove();
    field.removeAttribute('aria-describedby');
  };
  form.addEventListener('input', (e) => { if (e.target.matches('input, select, textarea')) clearError(e.target); });

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const f = form.elements;
    let first = null;
    const check = (field, ok, msg) => { if (!ok) { showError(field, msg); first ||= field; } };
    check(f.name, f.name.value.trim(), 'Enter your name.');
    check(f.email, /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.email.value.trim()), 'Enter an email address like name@company.com.');
    check(f.type, f.type.value, 'Choose the type of project.');
    check(f.message, f.message.value.trim().length >= 10, 'Describe the project in a sentence or two.');
    if (first) { first.focus(); status.textContent = ''; return; }

    // No backend yet: hand the request to the visitor's email app.
    const body = [
      `Name: ${f.name.value}`, `Company: ${f.company.value}`, `Email: ${f.email.value}`,
      `Phone: ${f.phone.value}`, `Project type: ${f.type.value}`, `Project location: ${f.location.value}`,
      '', f.message.value,
    ].join('\n');
    const subject = `Project request: ${f.type.value}`;
    window.location.href = `mailto:info@oritec.sa?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    status.textContent = 'Project request ready in your email app. Press send there to deliver it.';
  });

  /* ---------- Misc ---------- */
  const year = document.querySelector('[data-year]');
  if (year) year.textContent = new Date().getFullYear();

  const init = () => { sizeHorizontal(); drawTraces(); onScroll(); };
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(init); else window.addEventListener('load', init);
  window.addEventListener('load', init);
  init();
})();
