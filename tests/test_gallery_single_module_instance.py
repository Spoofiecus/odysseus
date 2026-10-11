"""Issue #6196: gallery.js was evaluated twice as two separate modules.

Module identity is keyed on the resolved URL. index.html loads
/static/js/gallery.js?v=... while app.js imported ./js/gallery.js without the
query, so the browser downloaded and evaluated the file twice, keeping two
copies of its state and two `gallery-refresh` listeners.
"""
import re
from pathlib import Path

INDEX = Path("static/index.html").read_text()
APP = Path("static/app.js").read_text()


def _index_src():
    match = re.search(r'<script type="module" src="(/static/js/gallery\.js[^"]*)"', INDEX)
    assert match, "gallery.js script tag not found in index.html"
    return match.group(1)


def _app_import():
    match = re.search(r"import galleryModule from '(\./js/gallery\.js[^']*)'", APP)
    assert match, "gallery import not found in app.js"
    return match.group(1)


def _query(url):
    return url.split("?", 1)[1] if "?" in url else ""


def test_gallery_module_urls_resolve_identically():
    assert _index_src().split("?")[0] == "/static/js/gallery.js"
    assert "/static/" + _app_import().split("?")[0].removeprefix("./") == "/static/js/gallery.js"
    assert _query(_index_src()) == _query(_app_import())
