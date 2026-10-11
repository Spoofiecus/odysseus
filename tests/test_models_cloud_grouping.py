"""Issue #6217: Ollama hosted models were grouped under "Local".

One Ollama endpoint serves both on-machine and hosted models; hosted ones carry
a `-cloud` / `:cloud` tag suffix and must be classified as remote (API).
"""
import re
import subprocess
from pathlib import Path

SOURCE = Path("static/js/models.js").read_text()


def test_cloud_tagged_models_are_remote():
    match = re.search(r"const modelRunsRemotely = (.*?);\n", SOURCE)
    assert match, "modelRunsRemotely helper not found"
    script = "const modelRunsRemotely = " + match.group(1) + ";\n" + r"""
function assert(c, m) { if (!c) throw new Error(m); }
assert(modelRunsRemotely('gpt-oss:120b-cloud') === true, 'dash-cloud');
assert(modelRunsRemotely('minimax-m3:cloud') === true, 'colon-cloud');
assert(modelRunsRemotely('nemotron-3-ultra:cloud') === true, 'colon-cloud-2');
assert(modelRunsRemotely('gemma3:12b') === false, 'local model');
assert(modelRunsRemotely('llama3.3:70b') === false, 'local model 2');
assert(modelRunsRemotely('') === false, 'empty');
"""
    subprocess.run(["node", "-e", script], check=True)


def test_grouping_uses_per_model_category():
    assert SOURCE.count("const cat = modelRunsRemotely(mid) ? 'api' : epCat;") == 2
