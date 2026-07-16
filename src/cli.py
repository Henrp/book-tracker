import argparse, re, sys
from fetcher import Fetcher, FetchError
from parser import parse_book
import storer

def book_id_from_url(url):
    m = re.search(r'/book/(?:[^/_]*_)?(\d+)', url)
    if not m:
        sys.exit(f"not a book URL: {url}")
    return m.group(1)

def cmd_add(con, f, args):
    bid = book_id_from_url(args.url)
    meta = parse_book(f.fetch_book_page(bid))
    if not meta:
        sys.exit("parse failed")
    storer.add_book(con, bid, meta)
    print(f"tracking: {meta['title']} — ch {meta['latest_chapter']}")

def cmd_check(con, f, args):
    for row in storer.get_tracked(con):
        bid = row["book_id"]
        try:
            meta = parse_book(f.fetch_book_page(bid))
        except FetchError as e:
            print(f"fetch failed {bid}: {e}", file=sys.stderr)
            continue
        if not meta or meta["latest_chapter"] is None:
            print(f"parse failed {bid}", file=sys.stderr)
            continue
        storer.update_progress(con, bid, meta)

def cmd_list(con, f, args):
    rows = storer.unread(con)
    if not rows:
        print("all caught up")
    for r in rows:
        print(f"{r['behind']:>4} new   {r['title']}  ({r['last_read']} → {r['last_known']})")

def cmd_read(con, f, args):
    storer.mark_read(con, book_id_from_url(args.url) if "/" in args.url else args.url,
                    args.chapter)

p = argparse.ArgumentParser()
sub = p.add_subparsers(dest="cmd", required=True)
a = sub.add_parser("add");   a.add_argument("url");                    a.set_defaults(fn=cmd_add)
c = sub.add_parser("check");                                           c.set_defaults(fn=cmd_check)
l = sub.add_parser("list");                                            l.set_defaults(fn=cmd_list)
r = sub.add_parser("read");  r.add_argument("url"); r.add_argument("chapter", type=int)
r.set_defaults(fn=cmd_read)

args = p.parse_args()
with storer.connect() as con:
    args.fn(con, Fetcher(), args)