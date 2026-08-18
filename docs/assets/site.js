// 医美技术栈 · 站点交互（原生 JS，无依赖）
document.documentElement.classList.add('js');

// 三栈浏览器标签切换
document.querySelectorAll('.stackx-tab').forEach(function (btn) {
  btn.addEventListener('click', function () {
    document.querySelectorAll('.stackx-tab').forEach(function (b) {
      b.classList.toggle('active', b === btn);
    });
    document.querySelectorAll('.stackx-pane').forEach(function (p) {
      p.classList.toggle('active', p.id === btn.dataset.target);
    });
  });
});

// 阅读进度条
(function () {
  var bar = document.querySelector('.progress-bar');
  if (!bar) return;
  function update() {
    var h = document.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    bar.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + '%';
  }
  window.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update);
  update();
})();

// 文章页侧目录 scrollspy
(function () {
  var links = Array.prototype.slice.call(document.querySelectorAll('.toc-rail a'));
  if (!links.length) return;
  var secs = links.map(function (a) {
    return document.getElementById(decodeURIComponent(a.hash.slice(1)));
  }).filter(Boolean);
  if (!secs.length || !('IntersectionObserver' in window)) return;
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      var id = e.target.id;
      links.forEach(function (l) {
        l.classList.toggle('cur', decodeURIComponent(l.hash.slice(1)) === id);
      });
    });
  }, { rootMargin: '-18% 0px -72% 0px' });
  secs.forEach(function (s) { io.observe(s); });
})();
