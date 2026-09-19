# -*- coding: utf-8 -*-
"""业务服务层：取词、提交复习、统计、计划、词本、本地 AI 生成。"""
import math
from datetime import date, datetime, time, timedelta

from django.db.models import Count, Q
from django.utils import timezone as tz

from .models import ReviewState, StudyRecord, Word
from .ebbinghaus import apply_quality


def word_dict(word, user=None):
    d = {
        "id": word.id,
        "word": word.word,
        "phonetic": word.phonetic,
        "pos": word.pos,
        "meaning": word.meaning,
        "example": word.example,
        "example_cn": word.example_cn,
        "synonyms": word.synonyms or [],
        "freq_read": word.freq_read,
        "freq_listen": word.freq_listen,
        "freq_translate": word.freq_translate,
        "freq_write": word.freq_write,
        "freq_total": word.freq_total(),
        "difficulty": word.difficulty,
        "mnemonic": word.mnemonic or "",
        "collocations": word.collocations or [],
        "confusables": word.confusables or [],
    }
    if user is not None:
        st = get_state_or_none(user, word)
        if st is None or (st.stage <= 0 and st.correct_count == 0 and st.wrong_count == 0 and st.next_review_at is None):
            d.update({"is_new": True, "stage": 0, "ease": 2.5, "lapses": 0,
                      "wrong_count": 0, "correct_count": 0,
                      "next_review_at": None, "retention": 0})
        else:
            d.update({
                "is_new": st.is_new,
                "stage": st.stage,
                "ease": round(st.ease, 2),
                "lapses": st.lapses,
                "wrong_count": st.wrong_count,
                "correct_count": st.correct_count,
                "next_review_at": st.next_review_at.isoformat() if st.next_review_at else None,
                "retention": retention(st),
            })
    else:
        d.update({"is_new": True, "stage": 0, "lapses": 0, "retention": 0})
    return d


def retention(st):
    total = st.correct_count + st.wrong_count
    if total == 0:
        return 0
    return round(st.correct_count / total, 2)


def get_state(user, word):
    st, _ = ReviewState.objects.get_or_create(user=user, word=word)
    return st


def get_state_or_none(user, word):
    try:
        return ReviewState.objects.get(user=user, word=word)
    except ReviewState.DoesNotExist:
        return None

def get_states(user, words):
    sts = {s.word_id: s for s in ReviewState.objects.filter(user=user, word__in=words)}
    out = []
    for w in words:
        out.append(sts.get(w.id) or ReviewState(user=user, word=w))
    return out


def priority_of(word, st):
    """多权重推送：优先级 = 考频 × 难度 × 遗忘率。"""
    wrong = st.wrong_count if st else 0
    correct = st.correct_count if st else 0
    forget = 1.0
    if correct + wrong > 0:
        forget = 1.0 + (wrong / max(1, correct + wrong)) * 2.0
    if st and st.lapses:
        forget += st.lapses * 0.5
    freq = word.freq_total() or 1
    diff = word.difficulty or 1
    return freq * diff * forget


def reasons_of(word, st, topic=None):
    ft = word.freq_total()
    wrong = st.wrong_count if st else 0
    return {
        "priority": round(priority_of(word, st), 2),
        "freq_total": ft,
        "topic_freq": (word.freq_listen if topic == "listen" else
                       word.freq_translate if topic == "translate" else
                       word.freq_write if topic == "write" else word.freq_read),
        "difficulty": word.difficulty,
        "forgetting": round((1.0 + wrong * 0.5) if wrong else 1.0, 2),
    }


def unseen_words(user):
    from django.db.models import Q as _Q
    studied = set(ReviewState.objects.filter(user=user).filter(
        _Q(stage__gt=0) | _Q(correct_count__gt=0) | _Q(wrong_count__gt=0)).values_list("word_id", flat=True))
    studied |= set(StudyRecord.objects.filter(user=user).values_list("word_id", flat=True))
    return Word.objects.exclude(id__in=studied)


def today_words(user, limit=40):
    now = tz.now()
    states = list(ReviewState.objects.filter(user=user).select_related("word"))
    due = [s for s in states if s.next_review_at and s.next_review_at <= now and (s.stage > 0 or s.correct_count > 0 or s.wrong_count > 0)]
    due.sort(key=lambda s: (-priority_of(s.word, s), s.next_review_at))
    new_qs = list(unseen_words(user).order_by("-freq_read", "word"))
    items = []
    for s in due[: max(0, limit)]:
        w = s.word
        wd = word_dict(w, user)
        wd["is_new"] = False
        wd["reason"] = reasons_of(w, s)
        items.append(wd)
    for w in new_qs[: max(0, limit - len(items))]:
        wd = word_dict(w, user)
        wd["is_new"] = True
        wd["reason"] = reasons_of(w, get_state_or_none(user, w))
        items.append(wd)
    return items


def submit(user, word_id, quality, review_type="learn", topic="", is_correct=True):
    try:
        word = Word.objects.get(id=word_id)
    except Word.DoesNotExist:
        return None
    st = get_state(user, word)
    plan = apply_quality(word, st, int(quality))
    StudyRecord.objects.create(
        user=user, word=word, quality=int(quality),
        review_type=review_type or "learn", topic=topic or "",
        is_correct=bool(is_correct),
    )
    return plan


def day_start(d=None):
    d = d or tz.localdate()
    return tz.make_aware(datetime.combine(d, time.min))


def day_end(d=None):
    return day_start(d) + timedelta(days=1)


def records_between(user, start, end):
    return StudyRecord.objects.filter(user=user, answered_at__gte=start, answered_at__lt=end)


def stats_summary(user, today=None):
    today = today or tz.localdate()
    ds, de = day_start(today), day_end(today)
    all_records = StudyRecord.objects.filter(user=user)
    learned = ReviewState.objects.filter(user=user).exclude(correct_count=0, wrong_count=0)
    mastered = ReviewState.objects.filter(user=user, stage__gte=5)
    now = tz.now()
    due = ReviewState.objects.filter(user=user, next_review_at__lte=now)
    stubborn = ReviewState.objects.filter(user=user).filter(Q(lapses__gte=3) | Q(wrong_count__gte=3))
    wrong_words = ReviewState.objects.filter(user=user, wrong_count__gt=0)
    total_records = all_records.count()
    correct_records = all_records.filter(is_correct=True).count()

    # 连续学习天数
    days = set(all_records.values_list("answered_at__date", flat=True))
    streak = 0
    d = today
    while d in days:
        streak += 1
        d -= timedelta(days=1)

    today_recs = records_between(user, ds, de)
    # 题型统计
    topic_rows = []
    for t in ("read", "listen", "translate", "write"):
        qs = all_records.filter(topic=t)
        n = qs.count()
        ok = qs.filter(is_correct=True).count()
        if n:
            topic_rows.append({"topic": t, "total": n, "correct": ok,
                               "accuracy": round(ok / n, 2)})
    # 近 7 天
    daily = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        n = records_between(user, day_start(d), day_end(d)).count()
        daily.append({"date": d.isoformat(), "count": n})

    return {
        "learned_total": learned.count(),
        "mastered": mastered.count(),
        "due_today": due.count(),
        "new_remaining": unseen_words(user).count(),
        "streak_days": streak,
        "accuracy": round(correct_records / total_records, 2) if total_records else 0,
        "wrong_count": wrong_words.count(),
        "stubborn_count": stubborn.count(),
        "topics": topic_rows,
        "plan_done": today_recs.filter(review_type__in=["learn", "review"]).count(),
        "plan_total": 0,
        "daily": daily,
    }


def notebook_items(user, kind="wrong", limit=200):
    states = ReviewState.objects.filter(user=user).select_related("word")
    if kind == "stubborn":
        states = states.filter(Q(lapses__gte=3) | Q(wrong_count__gte=3))
    else:
        states = states.filter(wrong_count__gt=0)
    states = states.order_by("-updated_at")[:limit]
    out = []
    for st in states:
        w = st.word
        last = StudyRecord.objects.filter(user=user, word=w, is_correct=False).order_by("-answered_at").first()
        out.append({
            "word": word_dict(w, user),
            "wrong_count": st.wrong_count,
            "lapses": st.lapses,
            "last_wrong_at": last.answered_at.isoformat() if last else None,
        })
    return out


def plan_daily(user, d=None, refresh=False):
    if isinstance(d, str) and d:
        try:
            d = date.fromisoformat(d[:10])
        except ValueError:
            d = None
    d = d or tz.localdate()
    ds, de = day_start(d), day_end(d)
    now = tz.now()
    states = list(ReviewState.objects.filter(user=user).select_related("word"))
    learn_new = []
    for w in list(unseen_words(user).order_by("-freq_read", "word"))[:10]:
        st = get_state_or_none(user, w)
        learn_new.append({"kind": "learn", "word": word_dict(w, user),
                          "reasons": reasons_of(w, st)})
    due = [s for s in states if s.next_review_at and s.next_review_at <= now and (s.stage > 0 or s.correct_count > 0 or s.wrong_count > 0)]
    due.sort(key=lambda s: (-priority_of(s.word, s), s.next_review_at))
    review, stubborn = [], []
    for s in due:
        wd = word_dict(s.word, user)
        wd["is_new"] = False
        item = {"kind": "review", "word": wd, "reasons": reasons_of(s.word, s)}
        if s.is_stubborn:
            item["kind"] = "stubborn"
            stubborn.append(item)
        else:
            review.append(item)
    review = review[:15]
    stubborn = stubborn[:10]

    # forecast: 未来7天到期数量
    forecast = []
    for i in range(1, 8):
        day = d + timedelta(days=i)
        nxt = tz.make_aware(datetime.combine(day, time.min))
        n = sum(1 for s in states if s.next_review_at and s.next_review_at < nxt + timedelta(days=1))
        forecast.append({"date": day.isoformat(), "total": n})

    today_recs = records_between(user, ds, de)
    plan_ids = {it["word"]["id"] for it in learn_new + review + stubborn}
    completed = today_recs.filter(word_id__in=plan_ids).values("word_id").distinct().count()
    total = len(learn_new) + len(review) + len(stubborn)
    return {
        "date": d.isoformat(),
        "completed": completed,
        "total": total,
        "progress": round(completed / total, 2) if total else 0,
        "learn_new": learn_new,
        "review": review,
        "stubborn": stubborn,
        "forecast": forecast,
    }


def word_search(user, q="", topic="", learned=0, sort="word", page=1, size=30):
    words = Word.objects.all()
    if q:
        words = words.filter(Q(word__icontains=q) | Q(meaning__icontains=q))
    if topic:
        field = {"read": "freq_read", "listen": "freq_listen",
                 "translate": "freq_translate", "write": "freq_write"}[topic]
        words = words.filter(**{field + "__gt": 0})
    if learned == 1:
        words = words.filter(id__in=ReviewState.objects.filter(user=user).values("word_id"))
    elif learned == 2:
        words = words.exclude(id__in=ReviewState.objects.filter(user=user).values("word_id"))
    if sort == "freq":
        words = words.order_by("-freq_read")
    elif sort == "difficulty":
        words = words.order_by("-difficulty")
    elif sort == "new":
        # 未学优先：已学排后
        learned_ids = list(ReviewState.objects.filter(user=user).values_list("word_id", flat=True))
        words = sorted(words, key=lambda w: (w.id in learned_ids, w.word))
        total = len(words)
        start = (page - 1) * size
        items = words[start:start + size]
        return {"total": total, "page": page, "size": size,
                "items": [word_dict(w, user) for w in items]}
    total = words.count()
    start = (page - 1) * size
    items = [word_dict(w, user) for w in words[start:start + size]]
    return {"total": total, "page": page, "size": size, "items": items}


def local_examples(word, count=2):
    ex = []
    if word.example:
        ex.append({"en": word.example, "cn": word.example_cn or ""})
    # 本地模板句（可离线演示；配置大模型 Key 后由 LLM 增强）
    import random
    templates = [
        ("Please {v} the main idea of this passage.", "请{v}这段话的主旨。"),
        ("It is important to {v} in daily life.", "在日常生活中{v}很重要。"),
    ]
    base = word.pos and word.pos.split("/")[0]
    for i in range(count - len(ex)):
        t = templates[i % len(templates)]
        verb = word.word if base in ("v", "vt", "vi") else ("use \"" + word.word + "\"")
        cn_verb = "理解" if base in ("v", "vt", "vi") else ("使用 “" + word.word + "”")
        ex.append({"en": t[0].format(v=verb), "cn": t[1].format(v=cn_verb)})
    return ex[:count]


def pick_words_for_train(user, topic="read", word=None, stubborn_only=False, count=4):
    """按题型/顽固词挑选训练用词。"""
    if word:
        w = Word.objects.filter(word=word).first()
        return [w] if w else []
    if stubborn_only:
        states = ReviewState.objects.filter(user=user).filter(
            Q(lapses__gte=3) | Q(wrong_count__gte=3)).select_related("word")
        return [s.word for s in states[:count]]
    field = {"read": "freq_read", "listen": "freq_listen",
             "translate": "freq_translate", "write": "freq_write"}.get(topic, "freq_read")
    qs = Word.objects.order_by("-" + field, "word")
    # 优先未学/近期复习词
    learned_ids = list(ReviewState.objects.filter(user=user).values_list("word_id", flat=True))
    new_first = list(qs.filter(~Q(id__in=learned_ids))[:count])
    if len(new_first) < count:
        more = list(qs.exclude(id__in=[w.id for w in new_first])[: count - len(new_first)])
        new_first += more
    return new_first


def build_train_questions(user, topic="read", word=None, stubborn_only=False, count=4):
    words = pick_words_for_train(user, topic, word, stubborn_only, count)
    questions = []
    for w in words:
        st = get_state_or_none(user, w)
        wd = word_dict(w, user)
        if topic == "listen":
            # 听音选义：前端负责朗读 word
            others = [x for x in words if x.id != w.id]
            opts = [w.meaning] + [x.meaning for x in others[:3]]
            questions.append({
                "type": "choice", "topic": topic,
                "stem": w.word, "listen": True,
                "options": opts, "answer": w.meaning,
                "explanation": w.pos + " " + w.meaning + ("；例：" + w.example if w.example else ""),
                "word_id": w.id, "word": w.word, "difficulty": w.difficulty,
            })
        elif topic == "translate":
            questions.append({
                "type": "typing", "topic": topic,
                "stem": w.meaning, "hint": w.pos,
                "options": [], "answer": w.word,
                "explanation": w.phonetic + " " + w.pos + " " + w.meaning,
                "word_id": w.id, "word": w.word, "difficulty": w.difficulty,
            })
        elif topic == "write":
            first = w.word[0].upper() if w.word else ""
            questions.append({
                "type": "typing", "topic": topic,
                "stem": "拼写单词：" + w.meaning, "hint": "首字母 " + first,
                "options": [], "answer": w.word,
                "explanation": w.phonetic + " " + w.pos + " " + w.meaning,
                "word_id": w.id, "word": w.word, "difficulty": w.difficulty,
            })
        else:  # read 英译汉
            others = [x for x in words if x.id != w.id]
            opts = [w.meaning] + [x.meaning for x in others[:3]]
            questions.append({
                "type": "choice", "topic": topic,
                "stem": w.word, "hint": w.phonetic + " " + w.pos,
                "options": opts, "answer": w.meaning,
                "explanation": w.pos + " " + w.meaning + ("；例：" + w.example if w.example else ""),
                "word_id": w.id, "word": w.word, "difficulty": w.difficulty,
            })
    # 打乱选项顺序
    import random
    for q in questions:
        if q["options"]:
            random.shuffle(q["options"])
    return questions


def local_planner(user):
    s = stats_summary(user)
    topics = {t["topic"]: t for t in s["topics"]}
    weak = [k for k in ("listen", "translate", "write", "read")
            if k in topics and topics[k]["accuracy"] < 0.6]
    strong = [k for k in ("listen", "translate", "write", "read")
              if k in topics and topics[k]["accuracy"] >= 0.75]
    advice = []
    if s["new_remaining"] > 0:
        advice.append("还有 %d 个新词未学，建议每天新学 8-10 个并坚持复习。" % s["new_remaining"])
    if s["due_today"] > 0:
        advice.append("今日有 %d 个复习任务，优先完成到期复习可避免遗忘。" % s["due_today"])
    if weak:
        advice.append("「%s」是你的薄弱题型，建议用对应题型专项训练加强。" % ("、".join(weak)))
    if s["stubborn_count"] > 0:
        advice.append("有 %d 个顽固词，建议进入 AI-训练评估做顽固词特训。" % s["stubborn_count"])
    if not advice:
        advice.append("保持当前节奏即可，注意艾宾浩斯到期复习不要中断。")
    return {
        "summary": "共学习 %d 词，掌握 %d 词，正确率 %d%%，连续学习 %d 天。" % (
            s["learned_total"], s["mastered"], round(s["accuracy"] * 100), s["streak_days"]),
        "strengths": strong or ["继续巩固现有优势题型"],
        "weaknesses": weak or ["无明显短板"],
        "advice": advice,
        "stats": s,
        "note": "本地结构化分析（未配置大模型 Key，可离线演示）",
    }


def local_tutor(user, word):
    w = Word.objects.filter(word=word).first()
    if not w:
        return None
    return {
        "word": w.word,
        "meaning": w.meaning,
        "phonetic": w.phonetic,
        "pos": w.pos,
        "explanation": (w.pos + " " + w.meaning) if w.pos else w.meaning,
        "mnemonic": w.mnemonic or ("拆词联想：\"" + w.word + "\" 结合例句记忆更牢固。"),
        "collocations": w.collocations or [],
        "confusable": w.confusables or [],
        "usage": w.example or "",
        "example_cn": w.example_cn or "",
        "note": "本地讲解（未配置大模型 Key）",
    }


def local_analyze(user, word):
    w = Word.objects.filter(word=word).first()
    if not w:
        return None
    st = get_state_or_none(user, w)
    if st is None or (st.wrong_count == 0 and st.correct_count == 0):
        return {"word": w.word, "analysis": "尚未学习过该词，建议先加入背诵。", "note": "本地分析"}
    reason = []
    if st.lapses >= 3:
        reason.append("多次遗忘（%d 次），建议进入顽固词特训并配合例句记忆。" % st.lapses)
    if st.wrong_count >= 3:
        reason.append("错误较多（%d 次），可能混淆形近词或释义，建议查看易混词与搭配。" % st.wrong_count)
    if not reason:
        reason.append("偶发错误，按艾宾浩斯间隔正常复习即可巩固。")
    return {
        "word": w.word,
        "analysis": "；".join(reason),
        "suggestion": ("联想记忆：" + w.mnemonic) if w.mnemonic else "结合例句朗读加深印象。",
        "note": "本地分析（未配置大模型 Key）",
    }