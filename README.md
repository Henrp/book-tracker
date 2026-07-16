## Setup

Requires Python 3.10+.

```
git clone https://github.com/Henrp/book-tracker.git
cd book-tracker
pip install -r requirements.txt
```

## Usage

### Web UI

```
cd src
python3 server.py
```

Open `http://127.0.0.1:5550`. Paste a book URL to start tracking it, click a cover to mark it caught up to the latest known chapter, or use the number field to set a specific chapter.

### CLI

From `src/`:

```
python3 cli.py add <book url>      # start tracking a book
python3 cli.py check               # refresh latest-chapter counts for all tracked books
python3 cli.py list                # show books with unread chapters
python3 cli.py read <book url|id> <chapter>   # record progress
```

Both the CLI and the web UI share the same `tracker.db` SQLite file in `src/`.
