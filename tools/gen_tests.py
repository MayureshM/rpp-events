#!/usr/bin/env python3
# tools/gen_tests.py
import ast, os, pathlib, re, textwrap

SRC_DIRS = ["src", "app", "package", "pkg", "."]  # adjust if needed
TEST_ROOT = "tests"

def discover_py_files():
    root = pathlib.Path(".").resolve()
    files = []
    for d in SRC_DIRS:
        p = root / d
        if not p.exists(): continue
        for f in p.rglob("*.py"):
            # Skip obvious test/migration/venv files
            if "tests" in f.parts or "site-packages" in f.parts or f.name.startswith("_"):
                continue
            files.append(f)
    return files

def parse_exports(pyfile: pathlib.Path):
    tree = ast.parse(pyfile.read_text(encoding="utf-8"))
    exports = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            if not node.name.startswith("_"):
                exports.append(("func", node.name, node))
        elif isinstance(node, ast.ClassDef):
            if not node.name.startswith("_"):
                exports.append(("class", node.name, node))
    return exports

def test_path_for(src_path: pathlib.Path):
    # mirror path under tests/
    rel = src_path.as_posix()
    rel = re.sub(r"^(src|app|package|pkg)/", "", rel)
    tpath = pathlib.Path(TEST_ROOT) / pathlib.Path(rel).with_suffix("")
    tfile = tpath.parent / f"test_{tpath.name}.py"
    return tfile

def ensure_header():
    pathlib.Path(TEST_ROOT).mkdir(exist_ok=True)
    (pathlib.Path(TEST_ROOT) / "__init__.py").touch()

TEST_TEMPLATE_FUNC = """\
import pytest
from {import_mod} import {name}

def test_{name}_happy_path():
    # TODO: replace with meaningful inputs/expected
    result = {name}(...)  # type: ignore
    assert result is not None

@pytest.mark.parametrize("bad", [None, ...])
def test_{name}_invalid_inputs(bad):
    with pytest.raises(Exception):
        {name}(bad)  # type: ignore

# Property-based skeleton (enable after choosing strategies)
# from hypothesis import given, strategies as st
# @given(st.just(...))
# def test_{name}_properties(x):
#     assert {name}(x) == {name}(x)
"""

TEST_TEMPLATE_CLASS = """\
import pytest
from {import_mod} import {name}

def test_{name}_basic_instantiation():
    obj = {name}(...)  # type: ignore
    assert obj is not None
"""

def module_import_path(src_path: pathlib.Path):
    # crude but effective: turn path to dotted import
    rel = src_path.with_suffix("").as_posix()
    rel = re.sub(r"^./", "", rel)
    rel = re.sub(r"/", ".", rel)
    return rel

def write_test(file: pathlib.Path, src_path: pathlib.Path, exports):
    file.parent.mkdir(parents=True, exist_ok=True)
    import_mod = module_import_path(src_path)
    lines = []
    for kind, name, _ in exports:
        if kind == "func":
            lines.append(TEST_TEMPLATE_FUNC.format(import_mod=import_mod, name=name))
        else:
            lines.append(TEST_TEMPLATE_CLASS.format(import_mod=import_mod, name=name))
    if lines:
        if file.exists():
            # append new stubs without clobbering
            with open(file, "a", encoding="utf-8") as f:
                f.write("\n\n" + "\n\n".join(lines))
        else:
            with open(file, "w", encoding="utf-8") as f:
                f.write("\n\n".join(lines))

def main():
    ensure_header()
    for py in discover_py_files():
        exports = parse_exports(py)
        if not exports: continue
        tfile = test_path_for(py)
        write_test(tfile, py.with_suffix(""), exports)
    print("✅ Test stubs generated under ./tests")

if __name__ == "__main__":
    main()
