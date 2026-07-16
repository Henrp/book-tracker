import html

import storer

CARD = """
<div class="card">
  <a class="cover-link" href="/read/{book_id}/{last_known}" title="Mark caught up to ch. {last_known}">
    <img class="cover" src="{cover_url}" alt="" referrerpolicy="no-referrer" onerror="this.style.visibility='hidden'">
  </a>
  <div class="info">
    <div class="title">{title}</div>
    <div class="author">{author}</div>
    <div class="bar"><div class="fill" style="width:{pct:.0f}%"></div></div>
    <div class="status {status_class}">{status_text}</div>
    <div class="meta">checked {last_checked}</div>
    <form class="progress" method="post" action="/read/{book_id}">
      <input type="number" name="chapter" value="{last_read}" min="0" max="{last_known}">
      <button type="submit">Set</button>
    </form>
  </div>
</div>
"""

PAGE = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Book Tracker</title>
<style>
  body {{ font-family: system-ui, sans-serif; background: #1a1a1e; color: #eee; margin: 0; padding: 2rem; }}
  h1 {{ font-weight: 600; margin-bottom: 1rem; }}
  form.add {{ display: flex; gap: 0.5rem; margin-bottom: 1.5rem; }}
  form.add input {{ flex: 1; max-width: 480px; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid #444; background: #26262b; color: #eee; }}
  form.add button {{ padding: 0.5rem 1rem; border-radius: 6px; border: none; background: #5b9dfa; color: #111; font-weight: 600; cursor: pointer; }}
  form.add button:hover {{ background: #7bb0fb; }}
  .error {{ background: #4a2323; color: #f5a3a3; padding: 0.6rem 0.9rem; border-radius: 6px; margin-bottom: 1rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; }}
  .card {{ display: flex; gap: 0.75rem; background: #26262b; border-radius: 8px; padding: 0.75rem; }}
  .cover {{ width: 56px; height: 76px; object-fit: cover; border-radius: 4px; background: #38383f; flex-shrink: 0; }}
  .info {{ min-width: 0; flex: 1; }}
  .title {{ font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .author {{ font-size: 0.85rem; color: #999; margin-bottom: 0.4rem; }}
  .bar {{ height: 6px; background: #38383f; border-radius: 3px; overflow: hidden; margin-bottom: 0.4rem; }}
  .fill {{ height: 100%; background: #5b9dfa; }}
  .status {{ font-size: 0.85rem; }}
  .status.behind {{ color: #f5a623; }}
  .status.caught-up {{ color: #4caf82; }}
  .meta {{ font-size: 0.75rem; color: #666; margin-top: 0.2rem; }}
  .empty {{ color: #888; }}
  .cover-link {{ display: block; flex-shrink: 0; }}
  .cover-link:hover .cover {{ outline: 2px solid #5b9dfa; }}
  form.progress {{ display: flex; gap: 0.4rem; margin-top: 0.4rem; }}
  form.progress input {{ width: 4.5rem; padding: 0.2rem 0.4rem; border-radius: 4px; border: 1px solid #444; background: #1a1a1e; color: #eee; }}
  form.progress button {{ padding: 0.2rem 0.6rem; border-radius: 4px; border: none; background: #38383f; color: #eee; cursor: pointer; }}
  form.progress button:hover {{ background: #48484f; }}
</style>
</head>
<body>
<h1>Book Tracker</h1>
{form}
{error}
<div class="grid">
{cards}
</div>
</body>
</html>
"""

ADD_FORM = """
<form class="add" method="post" action="/add">
  <input type="url" name="url" placeholder="Book URL (e.g. https://www.webnovel.com/book/x_123456)" required>
  <button type="submit">Add</button>
</form>
"""


def _render_cards(rows):
    if not rows:
        return '<div class="empty">no books tracked yet</div>'

    cards = []
    for r in rows:
        last_known = r["last_known"] or 0
        last_read = r["last_read"] or 0
        pct = min(100, (last_read / last_known * 100)) if last_known else 0
        behind = r["behind"] or 0
        if behind > 0:
            status_class, status_text = "behind", f"{behind} new chapter{'s' if behind != 1 else ''}"
        else:
            status_class, status_text = "caught-up", "caught up"
        cards.append(CARD.format(
            book_id=html.escape(r["book_id"]),
            cover_url=html.escape(r["cover_url"] or ""),
            title=html.escape(r["title"] or ""),
            author=html.escape(r["author"] or ""),
            pct=pct,
            status_class=status_class,
            status_text=html.escape(status_text),
            last_checked=html.escape(r["last_checked"] or "never"),
            last_known=last_known,
            last_read=last_read,
        ))
    return "\n".join(cards)


def build_page(con, error=None, show_form=False):
    rows = storer.all_active(con)
    error_html = f'<div class="error">{html.escape(error)}</div>' if error else ""
    return PAGE.format(
        form=ADD_FORM if show_form else "",
        error=error_html,
        cards=_render_cards(rows),
    )
