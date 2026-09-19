# -*- coding: utf-8 -*-
"""考频加权艾宾浩斯记忆排程（移植自 CT4项目1.0 算法设计）。"""
from django.utils import timezone
from datetime import timedelta

# 经典艾宾浩斯间隔（分钟）
EB_INTERVALS = [0, 10, 60, 1440, 4320, 10080, 21600, 43200, 86400, 172800]


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def freq_factor(word):
    """高频词因子 <1 → 复习更勤（间隔缩短）；低频 >1 → 拉长周期。"""
    ft = word.freq_total()
    return clamp(1.45 - 0.06 * ft, 0.5, 1.45)


def difficulty_factor(word):
    """难度越高越要勤复习。"""
    return clamp(1.0 + (word.difficulty - 2) * 0.15, 0.7, 1.45)


def next_interval(word, state, quality):
    """质量 0-5；>=3 视为认识。返回 (stage, interval_minutes)。"""
    if quality >= 3:
        stage = state.stage + 1
        base = EB_INTERVALS[min(stage, len(EB_INTERVALS) - 1)]
        # 首次学习间隔从 10 分钟起步，但至少给个短暂间隔
        if stage == 1:
            base = 10
        minutes = max(1, int(base * (state.ease / 2.5) * freq_factor(word) * difficulty_factor(word)))
    else:
        state.lapses += 1
        stage = max(0, state.stage - 1)
        minutes = 10
    return stage, minutes


def apply_quality(word, state, quality):
    """按质量更新记忆状态，返回 plan 字典。"""
    if quality >= 3:
        state.correct_count += 1
    else:
        state.wrong_count += 1
    state.last_quality = quality

    # ease 更新（类 Anki，简化）
    if quality >= 3:
        state.ease = clamp(state.ease + (0.1 - (5 - quality) * 0.08), 1.3, 3.0)
    else:
        state.ease = clamp(state.ease - 0.2, 1.3, 3.0)

    stage, minutes = next_interval(word, state, quality)
    state.stage = stage
    state.interval_minutes = minutes
    state.next_review_at = timezone.now() + timedelta(minutes=minutes)
    state.save()

    return {
        "word_id": word.id,
        "stage": state.stage,
        "ease": round(state.ease, 2),
        "interval_minutes": state.interval_minutes,
        "next_review_at": state.next_review_at.isoformat(),
        "lapses": state.lapses,
        "is_new": False,
        "wrong_count": state.wrong_count,
        "correct_count": state.correct_count,
    }