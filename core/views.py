# -*- coding: utf-8 -*-
"""CT4 Django JSON API（对应 CT4项目1.0 客户端 api 模块契约）。"""
import json

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .auth import do_login, login_required, make_token, user_payload
from .models import Word
from . import services as svc
from . import llm as llm


def body(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return {}


def ok(data, status=200):
    return JsonResponse(data, status=status)


def err(msg, status=400):
    return JsonResponse({"detail": msg}, status=status)


# ---------------- auth ----------------
@csrf_exempt
def register(request):
    b = body(request)
    username = (b.get("username") or "").strip()
    password = b.get("password") or ""
    nickname = (b.get("nickname") or "").strip()
    if len(username) < 3:
        return err("用户名至少 3 个字符")
    if len(password) < 6:
        return err("密码至少 6 位")
    if User.objects.filter(username=username).exists():
        return err("用户名已存在")
    user = User.objects.create_user(username=username, password=password)
    user.first_name = nickname or username
    user.save()
    return ok({"access_token": make_token(user), "user": user_payload(user)})


@csrf_exempt
def login(request):
    b = body(request)
    username = (b.get("username") or "").strip()
    password = b.get("password") or ""
    user = do_login(username, password)
    if user is None:
        return err("用户名或密码错误", 401)
    return ok({"access_token": make_token(user), "user": user_payload(user)})


@login_required
def me(request, user):
    return ok(user_payload(user))


# ---------------- words ----------------
@login_required
def words_today(request, user):
    limit = int(request.GET.get("limit") or 40)
    return ok({"items": svc.today_words(user, min(max(limit, 1), 200))})


@login_required
def words_list(request, user):
    data = svc.word_search(
        user,
        q=request.GET.get("q") or "",
        topic=request.GET.get("topic") or "",
        learned=int(request.GET.get("learned") or 0),
        sort=request.GET.get("sort") or "word",
        page=int(request.GET.get("page") or 1),
        size=int(request.GET.get("size") or 30),
    )
    return ok(data)


@login_required
def words_lookup(request, user):
    w = (request.GET.get("word") or "").strip().lower()
    word = Word.objects.filter(word__iexact=w).first()
    if not word:
        return err("词库中未找到该单词", 404)
    return ok(svc.word_dict(word, user))


@login_required
def word_detail(request, user, word_id):
    try:
        word = Word.objects.get(id=word_id)
    except Word.DoesNotExist:
        return err("单词不存在", 404)
    return ok(svc.word_dict(word, user))


# ---------------- records ----------------
@login_required
def record_submit(request, user):
    b = body(request)
    wid = b.get("word_id")
    if not wid:
        return err("缺少 word_id")
    plan = svc.submit(
        user, int(wid),
        quality=int(b.get("quality") or 3),
        review_type=b.get("review_type") or "learn",
        topic=b.get("topic") or "",
        is_correct=bool(b.get("is_correct", True)),
    )
    if plan is None:
        return err("单词不存在", 404)
    return ok(plan)


@login_required
def record_sync(request, user):
    records = body(request).get("records") or []
    results = []
    for r in records:
        if not r.get("word_id"):
            continue
        plan = svc.submit(
            user, int(r["word_id"]),
            quality=int(r.get("quality") or 3),
            review_type=r.get("review_type") or "learn",
            topic=r.get("topic") or "",
            is_correct=bool(r.get("is_correct", True)),
        )
        if plan:
            results.append(plan)
    return ok({"results": results, "synced": len(results)})


# ---------------- stats / plan / notebook ----------------
@login_required
def stats_summary(request, user):
    s = svc.stats_summary(user)
    plan = svc.plan_daily(user)
    s["plan_done"] = plan["completed"]
    s["plan_total"] = plan["total"]
    return ok(s)


@login_required
def plan_daily(request, user):
    d = request.GET.get("date") or None
    refresh = request.GET.get("refresh") == "1"
    return ok(svc.plan_daily(user, d, refresh))


@login_required
def notebook_wrong(request, user):
    limit = int(request.GET.get("limit") or 200)
    return ok({"items": svc.notebook_items(user, "wrong", limit)})


@login_required
def notebook_stubborn(request, user):
    limit = int(request.GET.get("limit") or 200)
    return ok({"items": svc.notebook_items(user, "stubborn", limit)})


@login_required
def notebook_summary(request, user):
    from django.db.models import Q
    wrong = svc.ReviewState.objects.filter(user=user, wrong_count__gt=0).count()
    stubborn = svc.ReviewState.objects.filter(user=user).filter(
        Q(lapses__gte=3) | Q(wrong_count__gte=3)).count()
    return ok({"wrong_total": wrong, "stubborn_total": stubborn})


# ---------------- AI / agents (本地结构化降级) ----------------
@login_required
def ai_example(request, user):
    b = body(request)
    wid = b.get("word_id")
    wname = (b.get("word") or "").strip()
    word = None
    if wid:
        word = Word.objects.filter(id=int(wid)).first()
    if word is None and wname:
        word = Word.objects.filter(word__iexact=wname).first()
    if word is None:
        return err("未在词库中找到该单词", 404)
    if llm.is_configured():
        try:
            text = llm.chat([
                {"role": "system", "content": "你是 CET-4 英语老师，为单词生成地道例句。只输出 JSON 数组，不要任何其他文字。"},
                {"role": "user", "content": "单词：%s (%s) 释义：%s。请给出 2 个不同场景的英文例句及中文翻译，格式：[{\"en\":\"英文\",\"cn\":\"中文\"}]" % (word.word, word.pos, word.meaning)},
            ])
            arr = llm.parse_json(text)
            if isinstance(arr, list):
                examples = []
                for x in arr[:3]:
                    if isinstance(x, dict) and str(x.get("en") or "").strip():
                        examples.append({"en": str(x["en"]).strip(), "cn": str(x.get("cn") or "").strip()})
                if examples:
                    return ok({"examples": examples, "note": "由 %s 生成" % llm.provider_label()})
        except Exception as e:
            return ok({"examples": svc.local_examples(word), "note": "大模型调用失败，已降级本地生成：" + str(e)})
    note = "本地例句生成（未配置大模型 Key）" if not llm.is_configured() else "大模型未返回有效例句，已降级本地生成"
    return ok({"examples": svc.local_examples(word), "note": note})


@login_required
def agent_plan(request, user):
    s = svc.stats_summary(user)
    local = svc.local_planner(user)
    if llm.is_configured():
        try:
            compact = {k: s.get(k) for k in ("learned_total", "mastered", "due_today", "new_remaining", "streak_days", "accuracy", "wrong_count", "stubborn_count", "plan_done", "plan_total")}
            compact["topics"] = s.get("topics") or []
            text = llm.chat([
                {"role": "system", "content": "你是 CET-4 学习规划师。必须只输出一个合法 JSON 对象，不要输出任何解释、注释或 Markdown。"},
                {"role": "user", "content": "根据我的学习统计生成规划：%s。JSON 结构固定为：{\"summary\":\"学情总结\",\"strengths\":[\"优势1\"],\"weaknesses\":[\"薄弱1\"],\"advice\":[\"建议1\",\"建议2\",\"建议3\"]}" % json.dumps(compact, ensure_ascii=False)},
            ])
            d = llm.parse_json(text)
            if isinstance(d, dict) and (d.get("advice") or d.get("summary")):
                def as_list(v, fallback):
                    if isinstance(v, list):
                        out = [str(x) for x in v if str(x).strip()][:6]
                        return out or fallback
                    return fallback
                return ok({
                    "summary": str(d.get("summary") or ("已学 %d 词，掌握 %d 词。" % (s["learned_total"], s["mastered"]))),
                    "strengths": as_list(d.get("strengths"), ["坚持学习即为优势"]),
                    "weaknesses": as_list(d.get("weaknesses"), ["无明显短板"]),
                    "advice": as_list(d.get("advice"), ["保持每日新学与复习节奏"]),
                    "stats": s,
                    "note": "由 %s 生成规划" % llm.provider_label(),
                })
            local["note"] = "大模型返回内容无法解析，已用本地规则生成规划"
            return ok(local)
        except Exception as e:
            local["note"] = "大模型调用失败，已降级本地：" + str(e)
            return ok(local)
    return ok(local)


@login_required
def agent_tutor(request, user):
    b = body(request)
    wname = (b.get("word") or "").strip()
    if not wname and b.get("word_id"):
        w = Word.objects.filter(id=int(b["word_id"])).first()
        wname = w.word if w else ""
    word = Word.objects.filter(word__iexact=wname).first()
    if word is None:
        return err("未在词库中找到该单词", 404)
    base = svc.local_tutor(user, word.word)
    if llm.is_configured():
        try:
            text = llm.chat([
                {"role": "system", "content": "你是 CET-4 词汇辅导老师，讲解要简明、适合背单词。只输出 JSON，不要其他文字。"},
                {"role": "user", "content": "词条：word=%s; phonetic=%s; pos=%s; meaning=%s; example=%s; synonyms=%s。输出 JSON：{\"explanation\":\"简明中文讲解\",\"mnemonic\":\"联想记忆\",\"collocations\":[\"搭配\"],\"confusable\":[\"易混词\"],\"usage\":\"英文例句\",\"example_cn\":\"例句中文\"}" % (word.word, word.phonetic, word.pos, word.meaning, word.example, ",".join(word.synonyms or []))},
            ])
            d = llm.parse_json(text)
            if isinstance(d, dict):
                for k in ("explanation", "mnemonic", "usage", "example_cn"):
                    if str(d.get(k) or "").strip():
                        base[k] = str(d[k]).strip()
                if isinstance(d.get("collocations"), list) and d["collocations"]:
                    base["collocations"] = [str(x) for x in d["collocations"] if str(x).strip()][:8]
                if isinstance(d.get("confusable"), list) and d["confusable"]:
                    base["confusable"] = [str(x) for x in d["confusable"] if str(x).strip()][:8]
                base["note"] = "由 %s 生成讲解" % llm.provider_label()
                return ok(base)
        except Exception as e:
            base["note"] = "大模型调用失败，已降级本地：" + str(e)
            return ok(base)
    return ok(base)


@login_required
def agent_train(request, user):
    b = body(request)
    topic = b.get("topic") or "read"
    questions = svc.build_train_questions(
        user, topic=topic,
        word=(b.get("word") or "").strip() or None,
        stubborn_only=bool(b.get("stubborn_only")),
        count=int(b.get("count") or 4),
    )
    if not questions:
        return err("没有可出题的单词（可先背诵积累或确认顽固词存在）", 400)
    return ok({"questions": questions, "topic": topic,
               "note": "本地出题引擎（例句/讲解/规划已接入大模型）"})


@login_required
def agent_analyze(request, user):
    b = body(request)
    wname = (b.get("word") or "").strip()
    if not wname and b.get("word_id"):
        w = Word.objects.filter(id=int(b["word_id"])).first()
        wname = w.word if w else ""
    word = Word.objects.filter(word__iexact=wname).first()
    if word is None:
        return err("未在词库中找到该单词", 404)
    wd = svc.word_dict(word, user)
    base = svc.local_analyze(user, word.word)
    if llm.is_configured():
        try:
            text = llm.chat([
                {"role": "system", "content": "你是 CET-4 错题分析老师。根据词条与学习情况输出 JSON，只输出 JSON 不要其他文字。"},
                {"role": "user", "content": "单词：%s (%s) 释义：%s。学习情况：遗忘 %d 次、答错 %d 次、答对 %d 次。输出 JSON：{\"analysis\":\"错因分析\",\"suggestion\":\"改进建议\"}" % (word.word, word.pos, word.meaning, wd["lapses"], wd["wrong_count"], wd["correct_count"])},
            ])
            d = llm.parse_json(text)
            if isinstance(d, dict) and (d.get("analysis") or d.get("suggestion")):
                if str(d.get("analysis") or "").strip():
                    base["analysis"] = str(d["analysis"]).strip()
                if str(d.get("suggestion") or "").strip():
                    base["suggestion"] = str(d["suggestion"]).strip()
                base["note"] = "由 %s 生成分析" % llm.provider_label()
                return ok(base)
        except Exception as e:
            base["note"] = "大模型调用失败，已降级本地：" + str(e)
            return ok(base)
    return ok(base)
# ---------------- public root / health ----------------
@csrf_exempt
def api_root(request):
    return ok({
        "project": "CT4 单词记忆",
        "backend": "Django 6.1.1",
        "frontend": "Vue 3.5.25 (Vite SPA)",
        "note": "前后端已解耦，本接口由 Django 提供",
        "endpoints": [
            "/api/auth/register", "/api/auth/login", "/api/auth/me",
            "/api/words/today", "/api/words", "/api/words/lookup", "/api/words/{id}",
            "/api/records", "/api/records/sync", "/api/stats/summary",
            "/api/plan/daily", "/api/notebook/wrong", "/api/notebook/stubborn",
            "/api/notebook/summary", "/api/ai/example",
            "/api/agents/plan", "/api/agents/tutor", "/api/agents/train", "/api/agents/analyze",
        ],
    })


@csrf_exempt
def health(request):
    return ok({"status": "ok", "time": timezone.now().isoformat()})
