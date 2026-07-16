import re

from flask import Flask, request, redirect, url_for

import storer
from fetcher import Fetcher, FetchError
from parser import parse_book
from render import build_page

app = Flask(__name__)
fetcher = Fetcher()


def book_id_from_url(url):
    m = re.search(r'/book/(?:[^/_]*_)?(\d+)', url)
    return m.group(1) if m else None


@app.route("/")
def index():
    con = storer.connect()
    return build_page(con, show_form=True)


@app.route("/add", methods=["POST"])
def add():
    url = request.form.get("url", "").strip()
    con = storer.connect()

    bid = book_id_from_url(url)
    if not bid:
        return build_page(con, error=f"not a book URL: {url}", show_form=True), 400

    try:
        meta = parse_book(fetcher.fetch_book_page(bid))
    except FetchError as e:
        return build_page(con, error=f"fetch failed: {e}", show_form=True), 502

    if not meta:
        return build_page(con, error="parse failed", show_form=True), 502

    storer.add_book(con, bid, meta)
    return redirect(url_for("index"))


@app.route("/read/<book_id>/<int:chapter>")
def read_full(book_id, chapter):
    con = storer.connect()
    storer.mark_read(con, book_id, chapter)
    return redirect(url_for("index"))


@app.route("/read/<book_id>", methods=["POST"])
def read_custom(book_id):
    con = storer.connect()
    try:
        chapter = int(request.form.get("chapter", ""))
    except ValueError:
        return build_page(con, error="invalid chapter number", show_form=True), 400
    storer.mark_read(con, book_id, chapter)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5550)

