"""Read-only Kaggle feed for the Biohub competition without a browser.

Discussions: the kagglesdk search API (ListEntities, TOPIC documents ordered by date) finds the competition's topics,
and the discussions API (GetTopic, ListComments) returns their full text and comments. Each topic is saved to
experiments/discussions/<id>.md; a digest of what is new since the previous run is printed and saved as
experiments/discussions/digest_<UTC>.md. State (seen comment ids per topic) lives in experiments/discussions/state.json.

Public notebooks: the same search API returns KERNEL documents with best_public_score, which the Kaggle CLI does not
show. --kernels prints the public biohub notebooks by score and flags any above --our-best (E10 v3 trigger check;
a flag is a signal to look, the trigger itself still needs the notebook page / runbook step 2).

Usage:
  python tools/kaggle_feed.py                 # discussions delta + kernels
  python tools/kaggle_feed.py --topics 60     # look at the newest 60 topics (default 40)
  python tools/kaggle_feed.py --no-kernels
Read-only: no post, vote, push or submit calls exist in this file.
"""
import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "experiments" / "discussions"
FORUM = "Biohub - Cell Tracking During Development"
COMP_URL = "/competitions/biohub-cell-tracking-during-development"
KERNEL_TITLE_EXCLUDE = ("xgboost", "lgbm", "optuna")  # other competitions whose titles also match 'biohub'


def _client():
    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    api.authenticate()
    return api.build_kaggle_client()


def _retry(fn, what, tries=6):
    for i in range(tries):
        try:
            return fn()
        except Exception as ex:  # noqa: BLE001 - network / 429 / 5xx
            msg = str(ex)
            if i == tries - 1 or not any(k in msg for k in ("429", "500", "502", "503", "timed out", "Connection")):
                raise
            print(f"  [retry {i + 1}] {what}: {msg[:120]}", file=sys.stderr)
            time.sleep(20 * (i + 1))


def _search(kc, doc_type, order, query, page_size, privacy=None):
    from kagglesdk.search.types.search_api_service import ListEntitiesFilters, ListEntitiesRequest

    r = ListEntitiesRequest()
    f = ListEntitiesFilters()
    f.query = query
    f.document_types = [doc_type]
    if privacy is not None:
        f.privacy = privacy
    r.filters = f
    r.canonical_order_by = order
    r.page_size = page_size
    return _retry(lambda: kc.search.search_api_client.list_entities(r), f"search {doc_type.name}").documents or []


def is_comp_topic(topic):
    """True for a topic of this competition's forum (the search also returns other forums)."""
    return (topic.get("forum_name") == FORUM) or (COMP_URL + "/discussion/") in (topic.get("url") or "")


def list_topics(kc, n):
    from kagglesdk.search.types.search_enums import DocumentType as D
    from kagglesdk.search.types.search_enums import ListSearchContentOrderBy as O

    ids = {}
    for order in (O.LIST_SEARCH_CONTENT_ORDER_BY_DATE_CREATED, O.LIST_SEARCH_CONTENT_ORDER_BY_DATE_UPDATED):
        for d in _search(kc, D.TOPIC, order, "biohub cell tracking", n):
            ids.setdefault(d.id, d.title)
    return ids


def fetch_topic(kc, tid, prev=None):
    """Topic text + all comments. If `prev` (state entry) has the same comment_count and last_comment_date, the comments
    are not re-listed and 'comments' is None (unchanged; saves one call per quiet topic)."""
    from kagglesdk.discussions.types.discussions_api_service import ApiGetTopicRequest, ApiListCommentsRequest

    c = kc.discussions.discussion_api_client
    r = ApiGetTopicRequest()
    r.id = tid
    t = _retry(lambda: c.get_topic(r), f"topic {tid}").topic
    head = {
        "id": tid, "title": t.title, "url": "https://www.kaggle.com" + (t.url or ""), "forum_name": t.forum_name,
        "author": t.author_name, "post_date": str(t.post_date), "last_comment_date": str(t.last_comment_date),
        "votes": t.votes, "comment_count": t.comment_count, "content": t.content or "", "comments": None,
    }
    if prev and prev.get("comment_count") == t.comment_count and prev.get("last_comment_date") == head["last_comment_date"]:
        return head
    comments, token = [], ""
    for _ in range(20):
        rq = ApiListCommentsRequest()
        rq.topic_id = tid
        rq.page_size = 100
        if token:
            rq.page_token = token
        resp = _retry(lambda: c.list_comments(rq), f"comments {tid}")
        comments.extend(resp.comments or [])
        token = resp.next_page_token or ""
        if not token:
            break
    head["comments"] = [_flat(x) for x in comments]
    return head


def _flat(cm, depth=0):
    out = {"id": cm.id, "author": cm.author_name, "date": str(cm.post_date), "votes": cm.votes,
           "content": cm.content or "", "depth": depth, "replies": []}
    for rp in cm.replies or []:
        out["replies"].append(_flat(rp, depth + 1))
    return out


def walk(comments):
    for cm in comments:
        yield cm
        yield from walk(cm["replies"])


def topic_md(t):
    lines = [f"# {t['title']}", "", f"{t['url']}  ", f"author {t['author']}, posted {t['post_date']}, votes {t['votes']}, "
             f"comments {t['comment_count']}, last comment {t['last_comment_date']}", "", t["content"].strip(), ""]
    for cm in walk(t["comments"]):
        ind = "  " * cm["depth"]
        lines += [f"{ind}---", f"{ind}**{cm['author']}** {cm['date']} (votes {cm['votes']}, id {cm['id']})", ""]
        lines += [ind + ln for ln in cm["content"].strip().splitlines()] + [""]
    return "\n".join(lines)


def delta(topic, seen_ids, since=""):
    """Return (is_new_topic, [new comments]).

    seen_ids None = the topic was never seen: it is new unless it was posted before `since` (first-run baseline), and
    its new comments are those dated at or after `since`. Otherwise the new comments are the ids not seen before.
    Dates compare as ISO strings ('2026-09-27 19:30:00...')."""
    if seen_ids is None:
        return topic["post_date"] >= since, [cm for cm in walk(topic["comments"]) if cm["date"] >= since]
    return False, [cm for cm in walk(topic["comments"]) if cm["id"] not in seen_ids]


def kernels(kc, our_best):
    from kagglesdk.search.types.search_enums import DocumentType as D
    from kagglesdk.search.types.search_enums import ListSearchContentOrderBy as O
    from kagglesdk.search.types.search_enums import PrivacyFilter as PF

    seen = {}
    for order in (O.LIST_SEARCH_CONTENT_ORDER_BY_DATE_UPDATED, O.LIST_SEARCH_CONTENT_ORDER_BY_VOTES,
                  O.LIST_SEARCH_CONTENT_ORDER_BY_DATE_CREATED):
        for d in _search(kc, D.KERNEL, order, "biohub", 50, privacy=PF.PUBLIC):
            if not d.kernel_document or any(k in d.title.lower() for k in KERNEL_TITLE_EXCLUDE):
                continue
            seen[d.id] = {"score": d.kernel_document.best_public_score or 0.0, "title": d.title,
                          "owner": d.owner_user.user_name if d.owner_user else "", "updated": str(d.update_time)[:16]}
    rows = sorted(seen.values(), key=lambda k: -k["score"])
    flags = [k for k in rows if k["score"] > our_best + 1e-9]
    return rows, flags


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--topics", type=int, default=40)
    ap.add_argument("--no-kernels", action="store_true")
    ap.add_argument("--our-best", type=float, default=0.959)
    ap.add_argument("--since", default="", help="first run only: report topics/comments dated at or after this "
                    "(e.g. '2026-09-27 18:00'); later runs report what was not seen before")
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    state_p = OUT / "state.json"
    state = json.loads(state_p.read_text(encoding="utf-8")) if state_p.exists() else {"topics": {}}
    first = state.get("last_run") is None
    since = a.since if first else ""
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%MZ")
    body, n_new_t, n_new_c = [], 0, 0
    with _client() as kc:
        cand = list_topics(kc, a.topics)
        for tid in sorted(cand, reverse=True):
            prev = state["topics"].get(str(tid))
            t = fetch_topic(kc, tid, prev)
            if not is_comp_topic(t) or t["comments"] is None:
                continue
            if first and not since:  # plain baseline
                new_topic, new_cm = False, []
            else:
                new_topic, new_cm = delta(t, None if prev is None else set(prev["comment_ids"]), since or "")
            (OUT / f"{tid}.md").write_text(topic_md(t), encoding="utf-8")
            state["topics"][str(tid)] = {"title": t["title"], "comment_ids": [c["id"] for c in walk(t["comments"])],
                                         "last_comment_date": t["last_comment_date"], "comment_count": t["comment_count"]}
            if new_topic:
                n_new_t += 1
                body += [f"## NEW TOPIC {tid}: {t['title']}", t["url"],
                         f"by {t['author']} {t['post_date']}, votes {t['votes']}", "", t["content"].strip(), ""]
            if new_cm:
                n_new_c += len(new_cm)
                body += [f"## NEW COMMENTS ({len(new_cm)}) on {tid}: {t['title']}", t["url"], ""]
                for cm in new_cm:
                    body += [f"- **{cm['author']}** {cm['date']} (votes {cm['votes']}):", "", cm["content"].strip(), ""]
        digest = [f"# Kaggle feed digest {now} (previous run {state.get('last_run') or 'none'})", "",
                  f"topics checked {len(cand)}; new topics {n_new_t}, new comments {n_new_c}"
                  + (f" (first run: counted from {since})" if first and since else " (first run: baseline only)"
                     if first else ""), ""] + body
        if not a.no_kernels:
            rows, flags = kernels(kc, a.our_best)
            digest += ["", f"## Public biohub notebooks by best_public_score (flag > {a.our_best})", ""]
            digest += [f"- {k['score']:.4f} {k['owner']} | {k['title']} | updated {k['updated']}" for k in rows[:15]]
            digest += ["", "E10 FLAG: " + ("; ".join(f"{k['owner']} '{k['title']}' {k['score']:.4f}" for k in flags)
                                           if flags else "none")]
    state["last_run"] = now
    state_p.write_text(json.dumps(state, indent=1), encoding="utf-8")
    text = "\n".join(digest)
    (OUT / f"digest_{now}.md").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
