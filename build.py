#!/usr/bin/env python3
"""Build static index.html from README.md"""
import re
import markdown
from markdown.extensions.toc import slugify_unicode
from pathlib import Path

ROOT = Path(__file__).parent
README = (ROOT / "README.md").read_text(encoding="utf-8")

lines = README.splitlines()
title = "Meta Muse AI 注册成功！用Gemini远程浏览器解决Meta最麻烦的一步"
body_md = README
if lines and lines[0].startswith("# "):
    title = lines[0][2:].strip()
    rest = lines[1:]
    if rest and rest[0].strip() == "":
        rest = rest[1:]
    body_md = "\n".join(rest) + ("\n" if README.endswith("\n") else "")

md = markdown.Markdown(
    extensions=["extra", "sane_lists", "toc"],
    extension_configs={"toc": {"permalink": False, "toc_depth": "2-3", "slugify": slugify_unicode}},
)
article_html = md.convert(body_md)


def slugify(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = text.strip().lower()
    text = re.sub(r"[^\w\u4e00-\u9fff\- ]+", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", "-", text)
    return text or "section"


def ensure_heading_ids(html: str) -> str:
    def repl(m):
        tag, attrs, content = m.group(1), m.group(2), m.group(3)
        if re.search(r"\bid\s*=", attrs):
            return m.group(0)
        sid = slugify(content)
        return f'<{tag} id="{sid}"{attrs}>{content}</{tag}>'

    return re.sub(r"<(h[23])([^>]*)>(.*?)</\1>", repl, html, flags=re.I | re.S)


article_html = ensure_heading_ids(article_html)


def enhance_images(html: str) -> str:
    def wrap_from_p(m):
        img_tag = m.group(1)
        src_m = re.search(r'src="([^"]+)"', img_tag)
        alt_m = re.search(r'alt="([^"]*)"', img_tag)
        if not src_m:
            return m.group(0)
        src = src_m.group(1)
        alt = alt_m.group(1) if alt_m else ""
        return (
            f'<figure class="img-card">'
            f'<img src="{src}" alt="{alt}" loading="lazy" decoding="async" '
            f'data-full="{src}" class="zoomable" />'
            f"</figure>"
        )

    html = re.sub(
        r"<p>\s*(<img\b[^>]*>)\s*</p>",
        wrap_from_p,
        html,
        flags=re.I | re.S,
    )

    def wrap_img(m):
        full = m.group(0)
        if "zoomable" in full:
            return full
        src_m = re.search(r'src="([^"]+)"', full)
        alt_m = re.search(r'alt="([^"]*)"', full)
        if not src_m:
            return full
        src = src_m.group(1)
        alt = alt_m.group(1) if alt_m else ""
        return (
            f'<figure class="img-card">'
            f'<img src="{src}" alt="{alt}" loading="lazy" decoding="async" '
            f'data-full="{src}" class="zoomable" />'
            f"</figure>"
        )

    html = re.sub(r"<img\b[^>]*>", wrap_img, html, flags=re.I)
    return html


article_html = enhance_images(article_html)

# Autolink bare URLs in text nodes (wording unchanged)
def autolink(html: str) -> str:
    parts = re.split(r"(<[^>]+>)", html)
    in_a = False
    for i, part in enumerate(parts):
        if part.startswith("<"):
            if re.match(r"<a\b", part, re.I):
                in_a = True
            elif re.match(r"</a>", part, re.I):
                in_a = False
            continue
        if not in_a:
            parts[i] = re.sub(r"(https?://[A-Za-z0-9./_\-?=&#%]+)",
                r'<a href="\1" target="_blank" rel="noopener noreferrer">\1</a>', part)
    return "".join(parts)

article_html = autolink(article_html)

toc_items = []
for m in re.finditer(
    r'<(h[23])\s+id="([^"]+)"[^>]*>(.*?)</\1>', article_html, flags=re.I | re.S
):
    level = m.group(1).lower()
    sid = m.group(2)
    text = re.sub(r"<[^>]+>", "", m.group(3)).strip()
    toc_items.append((level, sid, text))

toc_parts = [
    '<nav class="toc" id="toc" aria-label="目录">',
    '<div class="toc-header">',
    '<span class="toc-title">目录</span>',
    '<button type="button" class="toc-toggle" id="tocToggle" aria-expanded="false" aria-controls="tocList">展开</button>',
    "</div>",
    '<ol class="toc-list" id="tocList">',
]
for level, sid, text in toc_items:
    cls = "toc-h2" if level == "h2" else "toc-h3"
    toc_parts.append(f'<li class="{cls}"><a href="#{sid}">{text}</a></li>')
toc_parts.append("</ol></nav>")
toc_html = "\n".join(toc_parts)

desc = (
    "小编用 Gemini 远程浏览器成功注册 Meta Muse AI，绕过北美地区限制，"
    "并分享邀请码 0UWBGJ，免费领取 10 亿 Token。完整远程注册指南。"
)
og_image = "https://upload.maynor1024.live/file/1790612002490_muse-invite-0UWBGJ.png"
canonical = "https://xianyu110.github.io/muse/"

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <link rel="canonical" href="{canonical}" />
  <meta property="og:type" content="article" />
  <meta property="og:locale" content="zh_CN" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:image" content="{og_image}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title}" />
  <meta name="twitter:description" content="{desc}" />
  <meta name="twitter:image" content="{og_image}" />
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎭</text></svg>" />
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <div class="progress" id="progress" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0" aria-label="阅读进度"></div>

  <header class="hero">
    <div class="hero-inner">
      <p class="hero-badge">Meta Muse · 远程注册指南</p>
      <h1 class="hero-title">{title}</h1>
      <p class="hero-lead">用 Gemini 云端浏览器绕过地区限制，免费领取 10 亿 Token</p>

      <div class="invite-card" id="invite">
        <div class="invite-label">邀请码</div>
        <div class="invite-code-row">
          <code class="invite-code" id="inviteCode">0UWBGJ</code>
          <button type="button" class="btn btn-copy" id="copyBtn" aria-label="复制邀请码">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
            <span>复制</span>
          </button>
        </div>
        <a class="btn btn-join" href="https://muse.ai/join" target="_blank" rel="noopener noreferrer">前往 Muse 注册 →</a>
        <p class="invite-hint">双方各得 10 亿 Token · 最高可邀请 30 人</p>
      </div>
    </div>
  </header>

  <div class="layout">
    <aside class="sidebar">
      {toc_html}
    </aside>
    <main class="article" id="article">
      {article_html}
    </main>
  </div>

  <footer class="footer">
    <p><a href="https://github.com/xianyu110/muse">GitHub · xianyu110/muse</a></p>
  </footer>

  <button type="button" class="back-top" id="backTop" aria-label="回到顶部" title="回到顶部">↑</button>

  <div class="lightbox" id="lightbox" hidden>
    <button type="button" class="lightbox-close" id="lightboxClose" aria-label="关闭">×</button>
    <img src="" alt="" id="lightboxImg" />
  </div>

  <script src="app.js" defer></script>
</body>
</html>
"""

(ROOT / "index.html").write_text(html, encoding="utf-8")
(ROOT / ".nojekyll").write_text("", encoding="utf-8")
print("Built index.html")
print(f"TOC items: {len(toc_items)}")
for t in toc_items:
    print(" ", t)
