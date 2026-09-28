(function () {
  "use strict";
  var progress = document.getElementById("progress");
  var backTop = document.getElementById("backTop");
  var article = document.getElementById("article");

  function onScroll() {
    var doc = document.documentElement;
    var max = doc.scrollHeight - doc.clientHeight;
    var pct = max > 0 ? Math.min(100, (doc.scrollTop / max) * 100) : 0;
    progress.style.width = pct + "%";
    progress.setAttribute("aria-valuenow", Math.round(pct));
    backTop.classList.toggle("show", doc.scrollTop > 600);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  backTop.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });

  // copy invite code
  var copyBtn = document.getElementById("copyBtn");
  var code = document.getElementById("inviteCode").textContent.trim();
  function fallbackCopy(text) {
    var ta = document.createElement("textarea");
    ta.value = text; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0";
    document.body.appendChild(ta); ta.select();
    try { document.execCommand("copy"); } catch (e) {}
    document.body.removeChild(ta);
  }
  copyBtn.addEventListener("click", function () {
    var done = function () {
      var label = copyBtn.querySelector("span");
      copyBtn.classList.add("copied"); label.textContent = "已复制";
      setTimeout(function () { copyBtn.classList.remove("copied"); label.textContent = "复制"; }, 1800);
    };
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(code).then(done, function () { fallbackCopy(code); done(); });
    } else { fallbackCopy(code); done(); }
  });

  // TOC toggle (mobile)
  var toc = document.getElementById("toc");
  var toggle = document.getElementById("tocToggle");
  toggle.addEventListener("click", function () {
    var open = toc.classList.toggle("open");
    toggle.setAttribute("aria-expanded", open);
    toggle.textContent = open ? "收起" : "展开";
  });

  // TOC active highlight
  var links = Array.prototype.slice.call(toc.querySelectorAll("a"));
  var map = {};
  links.forEach(function (a) { map[decodeURIComponent(a.getAttribute("href").slice(1))] = a; });
  var headings = Array.prototype.slice.call(article.querySelectorAll("h2[id], h3[id]"));
  if ("IntersectionObserver" in window && headings.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          links.forEach(function (l) { l.classList.remove("active"); });
          var l = map[e.target.id]; if (l) l.classList.add("active");
        }
      });
    }, { rootMargin: "0px 0px -70% 0px" });
    headings.forEach(function (h) { io.observe(h); });
  }

  // lightbox
  var lb = document.getElementById("lightbox");
  var lbImg = document.getElementById("lightboxImg");
  function close() { lb.hidden = true; lbImg.src = ""; document.body.style.overflow = ""; }
  article.addEventListener("click", function (e) {
    var img = e.target.closest("img.zoomable");
    if (!img) return;
    lbImg.src = img.dataset.full || img.src; lbImg.alt = img.alt;
    lb.hidden = false; document.body.style.overflow = "hidden";
  });
  lb.addEventListener("click", close);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !lb.hidden) close(); });
})();
