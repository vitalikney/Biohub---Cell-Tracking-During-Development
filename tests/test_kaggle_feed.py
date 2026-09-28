import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import kaggle_feed as kf  # noqa: E402


def _cm(i, date, replies=()):
    return {"id": i, "author": "a", "date": date, "votes": 0, "content": "c%d" % i, "depth": 0, "replies": list(replies)}


def _topic(post_date, comments, forum=kf.FORUM, url="/competitions/biohub-cell-tracking-during-development/discussion/1"):
    return {"post_date": post_date, "comments": comments, "forum_name": forum, "url": url}


def test_walk_includes_nested_replies():
    t = [_cm(1, "2026-09-27 10:00", [_cm(2, "2026-09-27 11:00", [_cm(3, "2026-09-27 12:00")])]), _cm(4, "2026-09-28 01:00")]
    assert [c["id"] for c in kf.walk(t)] == [1, 2, 3, 4]


def test_delta_seen_topic_reports_only_unseen_ids():
    t = _topic("2026-09-01 00:00", [_cm(1, "2026-09-27 10:00", [_cm(2, "2026-09-28 04:00")]), _cm(3, "2026-09-28 05:00")])
    new_topic, new = kf.delta(t, {1})
    assert not new_topic and [c["id"] for c in new] == [2, 3]


def test_delta_unseen_topic_respects_since():
    t = _topic("2026-09-27 19:30", [_cm(1, "2026-09-27 10:00"), _cm(2, "2026-09-27 22:39")])
    new_topic, new = kf.delta(t, None, "2026-09-27 12:00")
    assert new_topic and [c["id"] for c in new] == [2]
    old = _topic("2026-09-01 00:00", [_cm(5, "2026-09-02 00:00")])
    new_topic, new = kf.delta(old, None, "2026-09-27 12:00")
    assert not new_topic and new == []


def test_is_comp_topic_filters_other_forums():
    assert kf.is_comp_topic(_topic("x", []))
    assert kf.is_comp_topic(_topic("x", [], forum="", url="/competitions/biohub-cell-tracking-during-development/discussion/9"))
    assert not kf.is_comp_topic(_topic("x", [], forum="Personal Writeups", url="/discussions/writeups/5"))


def test_topic_md_contains_all_comments():
    t = {"title": "T", "url": "u", "author": "x", "post_date": "p", "votes": 1, "comment_count": 2,
         "last_comment_date": "l", "content": "body", "comments": [_cm(1, "d1", [_cm(2, "d2")])]}
    md = kf.topic_md(t)
    assert "body" in md and "c1" in md and "c2" in md and "id 2" in md


def test_read_only_no_write_calls():
    """The feed must never post, vote, push or submit: only list/get/search client calls are allowed."""
    src = (Path(kf.__file__)).read_text(encoding="utf-8")
    calls = {n.func.attr for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    forbidden = {c for c in calls if any(w in c.lower() for w in ("create", "post", "vote", "submit", "push", "delete", "update_"))}
    assert not forbidden, forbidden
