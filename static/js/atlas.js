/* Core Radiology — Radiology Atlas
   互動層：側欄導覽、目錄高亮、閱讀進度、全書搜尋、醫學影像檢視器（縮放／平移／對比） */
(function () {
  'use strict';

  var doc = document;
  var body = doc.body;

  /* ================================================================
     1. 行動版側欄開合
     ================================================================ */
  (function sidebarToggle() {
    var toggle = doc.getElementById('atlas-menu-toggle');
    var scrim = doc.getElementById('atlas-sidebar-scrim');
    if (!toggle) return;

    function setOpen(open) {
      body.classList.toggle('atlas-sidebar-open', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    }
    toggle.addEventListener('click', function () {
      setOpen(!body.classList.contains('atlas-sidebar-open'));
    });
    if (scrim) scrim.addEventListener('click', function () { setOpen(false); });
    doc.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && body.classList.contains('atlas-sidebar-open')) setOpen(false);
    });
  })();

  /* ================================================================
     2. 章節摺疊（側欄）
     ================================================================ */
  (function chapterCollapse() {
    var chapters = doc.querySelectorAll('.atlas-chapter');
    Array.prototype.forEach.call(chapters, function (ch) {
      var btn = ch.querySelector('.atlas-chapter-btn');
      if (!btn) return;
      btn.addEventListener('click', function () {
        var open = ch.classList.toggle('is-open');
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
    });
  })();

  /* ================================================================
     3. 右側目錄（行動版抽屜）
     ================================================================ */
  (function tocDrawer() {
    var toggle = doc.getElementById('atlas-toc-toggle');
    var drawer = doc.getElementById('atlas-toc-mobile');
    if (!toggle || !drawer) return;

    // 將桌面版目錄複製到行動抽屜，避免伺服器重複輸出大型 TOC
    var source = doc.getElementById('atlas-toc');
    var target = doc.getElementById('atlas-toc-mobile-inner');
    if (source && target) {
      var clone = source.cloneNode(true);
      clone.removeAttribute('id');
      var marker = clone.querySelector('#toc-clone');
      if (marker) marker.parentNode.replaceChild(document.createComment('toc-clone'), marker);
      target.appendChild(clone);
    }

    function setOpen(open) {
      drawer.classList.toggle('is-open', open);
      drawer.setAttribute('aria-hidden', open ? 'false' : 'true');
    }
    toggle.addEventListener('click', function () { setOpen(!drawer.classList.contains('is-open')); });
    drawer.addEventListener('click', function (e) {
      if (e.target === drawer) setOpen(false);
    });
    doc.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && drawer.classList.contains('is-open')) setOpen(false);
    });
  })();

  /* ================================================================
     4. 閱讀進度 + 目錄高亮
     ================================================================ */
  (function readingProgress() {
    var article = doc.querySelector('.atlas-content');
    if (!article) return;

    var fills = doc.querySelectorAll('.atlas-progress-fill');
    var pcts = doc.querySelectorAll('[id^="atlas-progress-pct"]');
    var headings = Array.prototype.slice.call(
      article.querySelectorAll('h2[id], h3[id]')
    );

    function setProgress(pct) {
      var v = Math.max(0, Math.min(100, pct));
      Array.prototype.forEach.call(fills, function (f) { f.style.width = v + '%'; });
      Array.prototype.forEach.call(pcts, function (p) { p.textContent = Math.round(v) + '%'; });
    }

    function update() {
      var rect = article.getBoundingClientRect();
      var total = rect.height - window.innerHeight;
      var scrolled = -rect.top;
      var pct = total > 0 ? (scrolled / total) * 100 : (rect.top < 0 ? 100 : 0);
      setProgress(pct);
    }

    // 目錄高亮
    var tocLinks = Array.prototype.slice.call(
      doc.querySelectorAll('#TableOfContents a[href^="#"]')
    );
    var linkById = {};
    tocLinks.forEach(function (a) {
      var id = decodeURIComponent(a.getAttribute('href').slice(1));
      linkById[id] = a;
    });

    function highlight() {
      var offset = 120;
      var current = null;
      headings.forEach(function (h) {
        if (h.getBoundingClientRect().top <= offset) current = h.id;
      });
      if (!current && headings.length) current = headings[0].id;
      tocLinks.forEach(function (a) { a.classList.remove('is-active'); });
      var active = linkById[current];
      if (active) active.classList.add('is-active');
    }

    var ticking = false;
    function onScroll() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () {
        update();
        highlight();
        ticking = false;
      });
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    update();
    highlight();
  })();

  /* ================================================================
     5. 全書搜尋（純前端字串比對，避免額外相依）
     ================================================================ */
  (function search() {
    var input = doc.getElementById('atlas-search-input');
    var list = doc.getElementById('atlas-search-results');
    if (!input || !list) return;

    var index = null;
    var loading = false;
    var pending = [];

    function load() {
      if (index) return;
      if (loading) return;
      var url = list.getAttribute('data-search-index');
      if (!url) return;
      loading = true;
      fetch(url)
        .then(function (r) { return r.json(); })
        .then(function (data) {
          index = data;
          loading = false;
          var cbs = pending;
          pending = [];
          cbs.forEach(function (cb) { cb(); });
        })
        .catch(function () { loading = false; });
    }

    function whenReady(cb) {
      if (index) { cb(); return; }
      pending.push(cb);
      load();
    }

    function escapeHTML(s) {
      return String(s).replace(/[&<>"']/g, function (c) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
      });
    }

    function snippet(content, term) {
      var pos = content.toLowerCase().indexOf(term.toLowerCase());
      if (pos < 0) return escapeHTML(content.slice(0, 90)) + '…';
      var start = Math.max(0, pos - 40);
      var end = Math.min(content.length, pos + term.length + 60);
      var pre = escapeHTML(content.slice(start, pos));
      var hit = escapeHTML(content.slice(pos, pos + term.length));
      var post = escapeHTML(content.slice(pos + term.length, end));
      return (start > 0 ? '…' : '') + pre + '<mark>' + hit + '</mark>' + post + '…';
    }

    function run() {
      var term = input.value.trim();
      if (term.length < 2) { list.classList.remove('is-open'); list.innerHTML = ''; return; }
      if (!index) { whenReady(run); return; }

      var lower = term.toLowerCase();
      var hits = [];
      for (var i = 0; i < index.length && hits.length < 12; i++) {
        var page = index[i];
        var inTitle = page.title.toLowerCase().indexOf(lower) >= 0;
        var inSection = (page.section || '').toLowerCase().indexOf(lower) >= 0;
        var inContent = page.content.toLowerCase().indexOf(lower) >= 0;
        if (inTitle || inSection || inContent) {
          hits.push({ page: page, score: (inTitle ? 3 : 0) + (inSection ? 2 : 0) + (inContent ? 1 : 0) });
        }
      }
      hits.sort(function (a, b) { return b.score - a.score; });

      if (!hits.length) {
        list.innerHTML = '<li class="atlas-search-empty">找不到相符內容</li>';
        list.classList.add('is-open');
        return;
      }

      list.innerHTML = hits.map(function (h) {
        var p = h.page;
        return '<li><a href="' + escapeHTML(p.href) + '">' +
          '<span class="r-title">' + escapeHTML(p.title) + '</span>' +
          (p.section ? '<span class="r-section">' + escapeHTML(p.section) + '</span>' : '') +
          '<span class="r-hit">' + snippet(p.content, term) + '</span>' +
          '</a></li>';
      }).join('');
      list.classList.add('is-open');
    }

    var timer;
    input.addEventListener('input', function () {
      clearTimeout(timer);
      timer = setTimeout(run, 180);
    });
    input.addEventListener('focus', load);
    doc.addEventListener('click', function (e) {
      if (!list.contains(e.target) && e.target !== input) list.classList.remove('is-open');
    });
    doc.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { list.classList.remove('is-open'); input.blur(); }
    });
  })();

  /* ================================================================
     6. 醫學影像檢視器：放大／縮放／平移／雙圖對比
     ================================================================ */
  (function imageViewer() {
    var viewer = doc.getElementById('atlas-viewer');
    if (!viewer) return;

    var stage = doc.getElementById('atlas-viewer-stage');
    var paneA = doc.getElementById('atlas-viewer-pane-a');
    var paneB = doc.getElementById('atlas-viewer-pane-b');
    var imgA = doc.getElementById('atlas-viewer-img-a');
    var imgB = doc.getElementById('atlas-viewer-img-b');
    var caption = doc.getElementById('atlas-viewer-caption');
    var zoomLabel = doc.getElementById('atlas-viewer-zoom');
    var tray = doc.getElementById('atlas-viewer-tray');
    var thumbs = doc.getElementById('atlas-viewer-thumbs');

    var state = {
      open: false,
      compare: false,
      scale: 1,
      tx: 0,
      ty: 0,
      dragging: false,
      startX: 0,
      startY: 0,
      originX: 0,
      originY: 0,
      images: [],
      current: 0
    };

    function applyTransform(img) {
      img.style.transform = 'translate(' + state.tx + 'px,' + state.ty + 'px) scale(' + state.scale + ')';
    }

    function updateZoomLabel() {
      if (zoomLabel) zoomLabel.textContent = Math.round(state.scale * 100) + '%';
    }

    function resetTransform() {
      state.scale = 1;
      state.tx = 0;
      state.ty = 0;
      applyTransform(imgA);
      applyTransform(imgB);
      updateZoomLabel();
    }

    function setImage(src, cap, index) {
      state.current = index == null ? 0 : index;
      imgA.src = src;
      imgA.alt = cap || '';
      caption.textContent = cap || '';
      resetTransform();
    }

    function collectImages() {
      var map = [];
      var seen = {};
      Array.prototype.forEach.call(doc.querySelectorAll('.atlas-figure'), function (fig) {
        var src = fig.getAttribute('data-image-src');
        if (!src || seen[src]) return;
        seen[src] = true;
        var capEl = fig.querySelector('.atlas-figure-caption-text');
        map.push({ src: src, caption: capEl ? capEl.textContent.trim() : '' });
      });
      return map;
    }

    function openViewer(src, cap) {
      state.images = collectImages();
      var idx = 0;
      for (var i = 0; i < state.images.length; i++) {
        if (state.images[i].src === src) { idx = i; break; }
      }
      state.open = true;
      state.compare = false;
      paneB.classList.remove('is-visible');
      tray.classList.remove('is-open');
      setImage(src, cap, idx);
      viewer.classList.add('is-open');
      doc.documentElement.style.overflow = 'hidden';
      renderThumbs();
    }

    function closeViewer() {
      state.open = false;
      viewer.classList.remove('is-open');
      doc.documentElement.style.overflow = '';
    }

    function renderThumbs() {
      thumbs.innerHTML = state.images.map(function (im, i) {
        return '<button class="atlas-viewer-thumb' + (i === state.current ? ' is-active' : '') +
          '" type="button" data-thumb-index="' + i + '">' +
          '<img src="' + im.src + '" alt=""></button>';
      }).join('');
    }

    function toggleCompare(on) {
      state.compare = on;
      var btn = viewer.querySelector('[data-viewer-action="compare"]');
      if (on) {
        paneB.classList.add('is-visible');
        tray.classList.add('is-open');
        if (btn) btn.classList.add('is-active');
        var other = state.images.filter(function (im, i) { return i !== state.current; });
        if (other.length) {
          imgB.src = other[0].src;
          imgB.alt = other[0].caption;
          applyTransform(imgB);
        }
      } else {
        paneB.classList.remove('is-visible');
        tray.classList.remove('is-open');
        if (btn) btn.classList.remove('is-active');
      }
    }

    // 開啟觸發
    doc.addEventListener('click', function (e) {
      var opener = e.target.closest('[data-atlas-viewer-open]');
      if (opener) {
        e.preventDefault();
        openViewer(opener.getAttribute('data-atlas-viewer-open'), opener.getAttribute('data-atlas-caption'));
        return;
      }
      var compareBtn = e.target.closest('[data-atlas-compare]');
      if (compareBtn) {
        e.preventDefault();
        var src = compareBtn.getAttribute('data-atlas-compare');
        compareBtn.classList.toggle('is-armed');
        if (compareBtn.classList.contains('is-armed')) {
          openViewer(src, compareBtn.getAttribute('data-atlas-caption') || '');
          toggleCompare(true);
        }
        return;
      }
    });

    // 工具列
    viewer.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-viewer-action]');
      if (btn) {
        var action = btn.getAttribute('data-viewer-action');
        if (action === 'close') closeViewer();
        else if (action === 'zoom-in') { state.scale = Math.min(6, state.scale * 1.25); applyTransform(imgA); applyTransform(imgB); updateZoomLabel(); }
        else if (action === 'zoom-out') { state.scale = Math.max(0.2, state.scale / 1.25); applyTransform(imgA); applyTransform(imgB); updateZoomLabel(); }
        else if (action === 'reset') resetTransform();
        else if (action === 'compare') toggleCompare(!state.compare);
        else if (action === 'compare-off') toggleCompare(false);
        return;
      }
      var thumb = e.target.closest('[data-thumb-index]');
      if (thumb) {
        var i = parseInt(thumb.getAttribute('data-thumb-index'), 10);
        var im = state.images[i];
        if (!im) return;
        if (state.compare) {
          imgB.src = im.src;
          imgB.alt = im.caption;
          applyTransform(imgB);
        } else {
          setImage(im.src, im.caption, i);
        }
        state.current = i;
        renderThumbs();
      }
    });

    // 鍵盤
    doc.addEventListener('keydown', function (e) {
      if (!state.open) return;
      if (e.key === 'Escape') closeViewer();
      else if (e.key === '+' || e.key === '=') { state.scale = Math.min(6, state.scale * 1.25); applyTransform(imgA); applyTransform(imgB); updateZoomLabel(); }
      else if (e.key === '-') { state.scale = Math.max(0.2, state.scale / 1.25); applyTransform(imgA); applyTransform(imgB); updateZoomLabel(); }
      else if (e.key === '0') resetTransform();
      else if (e.key === 'ArrowRight') { var n = (state.current + 1) % state.images.length; setImage(state.images[n].src, state.images[n].caption, n); renderThumbs(); }
      else if (e.key === 'ArrowLeft') { var p = (state.current - 1 + state.images.length) % state.images.length; setImage(state.images[p].src, state.images[p].caption, p); renderThumbs(); }
    });

    // 滾輪縮放
    stage.addEventListener('wheel', function (e) {
      e.preventDefault();
      var delta = e.deltaY < 0 ? 1.12 : 1 / 1.12;
      state.scale = Math.max(0.2, Math.min(6, state.scale * delta));
      applyTransform(imgA);
      applyTransform(imgB);
      updateZoomLabel();
    }, { passive: false });

    // 拖曳平移（滑鼠 + 觸控）
    [paneA, paneB].forEach(function (pane) {
      pane.addEventListener('mousedown', function (e) {
        state.dragging = true;
        state.startX = e.clientX;
        state.startY = e.clientY;
        state.originX = state.tx;
        state.originY = state.ty;
        e.preventDefault();
      });
      pane.addEventListener('touchstart', function (e) {
        if (e.touches.length !== 1) return;
        state.dragging = true;
        state.startX = e.touches[0].clientX;
        state.startY = e.touches[0].clientY;
        state.originX = state.tx;
        state.originY = state.ty;
      }, { passive: true });
    });

    doc.addEventListener('mousemove', function (e) {
      if (!state.dragging) return;
      state.tx = state.originX + (e.clientX - state.startX);
      state.ty = state.originY + (e.clientY - state.startY);
      applyTransform(imgA);
      applyTransform(imgB);
    });
    doc.addEventListener('touchmove', function (e) {
      if (!state.dragging || e.touches.length !== 1) return;
      state.tx = state.originX + (e.touches[0].clientX - state.startX);
      state.ty = state.originY + (e.touches[0].clientY - state.startY);
      applyTransform(imgA);
      applyTransform(imgB);
    }, { passive: true });
    doc.addEventListener('mouseup', function () { state.dragging = false; });
    doc.addEventListener('touchend', function () { state.dragging = false; });

    // 雙擊 / 雙觸放大
    [paneA, paneB].forEach(function (pane) {
      pane.addEventListener('dblclick', function () {
        state.scale = state.scale > 1 ? 1 : 2.5;
        state.tx = 0;
        state.ty = 0;
        applyTransform(imgA);
        applyTransform(imgB);
        updateZoomLabel();
      });
    });
  })();

  /* ================================================================
     7. 表格水平捲動提示（行動版）
     ================================================================ */
  (function tableScrollHint() {
    Array.prototype.forEach.call(doc.querySelectorAll('.atlas-table-wrap'), function (wrap) {
      wrap.addEventListener('scroll', function () {
        wrap.classList.toggle('is-scrolled', wrap.scrollLeft > 4);
      });
    });
  })();
})();
