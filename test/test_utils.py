# Copyright 2017-2020 Palantir Technologies, Inc.
# Copyright 2021- Python Language Server Contributors.

import time
from unittest import mock

from flaky import flaky

from pylsp import _utils
from pylsp.python_lsp import korbit_custom_lints


@flaky(max_runs=6, min_passes=1)
def test_debounce():
    interval = 0.1
    obj = mock.Mock()

    @_utils.debounce(0.1)
    def call_m():
        obj()

    assert not obj.mock_calls

    call_m()
    call_m()
    call_m()
    assert not obj.mock_calls

    time.sleep(interval * 2)
    assert len(obj.mock_calls) == 1

    call_m()
    time.sleep(interval * 2)
    assert len(obj.mock_calls) == 2


@flaky(max_runs=6, min_passes=1)
def test_debounce_keyed_by():
    interval = 0.1
    obj = mock.Mock()

    @_utils.debounce(0.1, keyed_by='key')
    def call_m(key):
        obj(key)

    assert not obj.mock_calls

    call_m(1)
    call_m(2)
    call_m(3)
    assert not obj.mock_calls

    time.sleep(interval * 2)
    obj.assert_has_calls([
        mock.call(1),
        mock.call(2),
        mock.call(3),
    ], any_order=True)
    assert len(obj.mock_calls) == 3

    call_m(1)
    call_m(1)
    call_m(1)
    time.sleep(interval * 2)
    assert len(obj.mock_calls) == 4


def test_list_to_string():
    assert _utils.list_to_string("string") == "string"
    assert _utils.list_to_string(["a", "r", "r", "a", "y"]) == "a,r,r,a,y"


def test_find_parents(tmpdir):
    subsubdir = tmpdir.ensure_dir("subdir", "subsubdir")
    path = subsubdir.ensure("path.py")
    test_cfg = tmpdir.ensure("test.cfg")

    assert _utils.find_parents(tmpdir.strpath, path.strpath, ["test.cfg"]) == [test_cfg.strpath]


def test_merge_dicts():
    assert _utils.merge_dicts(
        {'a': True, 'b': {'x': 123, 'y': {'hello': 'world'}}},
        {'a': False, 'b': {'y': [], 'z': 987}}
    ) == {'a': False, 'b': {'x': 123, 'y': [], 'z': 987}}


def test_clip_column():
    assert _utils.clip_column(0, [], 0) == 0
    assert _utils.clip_column(2, ['123'], 0) == 2
    assert _utils.clip_column(3, ['123'], 0) == 3
    assert _utils.clip_column(5, ['123'], 0) == 3
    assert _utils.clip_column(0, ['\n', '123'], 0) == 0
    assert _utils.clip_column(1, ['\n', '123'], 0) == 0
    assert _utils.clip_column(2, ['123\n', '123'], 0) == 2
    assert _utils.clip_column(3, ['123\n', '123'], 0) == 3
    assert _utils.clip_column(4, ['123\n', '123'], 1) == 3


def test_korbit_custom_lints():
    lints = [
        {
            'source': "pyflakes",
            'range': {
                'start': {'line': 3, 'character': 19}, 'end': {'line': 3, 'character': 38}
            },
            'message': "EOL while scanning string literal",
            'severity': 1,
        },
        {
            'source': "pycodestyle",
            'range': {
                'start': {
                    'line': 3,
                    'character': 13
                },
                'end': {
                    'line': 3,
                    'character': 19
                }
            },
            'message': "E221 multiple spaces before operator",
            'severity': 2,
        }
    ]
    new_lints = korbit_custom_lints(lints)
    assert len(new_lints) == 1
    assert new_lints[0]['severity'] == 1


def test_korbit_custom_lints_between():
    lints = [
        {
            'source': "pyflakes",
            'range': {
                'start': {'line': 2, 'character': 19}, 'end': {'line': 5, 'character': 38}
            },
            'message': "EOL while scanning string literal",
            'severity': 1,
        },
        {
            'source': "pycodestyle",
            'range': {
                'start': {
                    'line': 3,
                    'character': 13
                },
                'end': {
                    'line': 3,
                    'character': 19
                }
            },
            'message': "E221 multiple spaces before operator",
            'severity': 2,
        }
    ]
    new_lints = korbit_custom_lints(lints)
    assert len(new_lints) == 1
    assert new_lints[0]['severity'] == 1


def test_korbit_custom_lints_warning():
    lints = [
        {
            'source': "pyflakes",
            'range': {
                'start': {'line': 2, 'character': 19}, 'end': {'line': 3, 'character': 38}
            },
            'message': "EOL while scanning string literal",
            'severity': 1,
        },
        {
            'source': "pycodestyle",
            'range': {
                'start': {
                    'line': 4,
                    'character': 13
                },
                'end': {
                    'line': 4,
                    'character': 19
                }
            },
            'message': "E221 multiple spaces before operator",
            'severity': 2,
        }
    ]
    new_lints = korbit_custom_lints(lints)
    assert len(new_lints) == 2
    assert new_lints[0]['severity'] == 1
    assert new_lints[1]['severity'] == 2
