from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    # public
    path("api/health", views.health, name="health"),
    path("api", views.api_root, name="api_root"),
    # auth
    path("api/auth/register", views.register, name="register"),
    path("api/auth/login", views.login, name="login"),
    path("api/auth/me", views.me, name="me"),
    # words
    path("api/words/today", views.words_today, name="words_today"),
    path("api/words/lookup", views.words_lookup, name="words_lookup"),
    path("api/words", views.words_list, name="words_list"),
    path("api/words/<int:word_id>", views.word_detail, name="word_detail"),
    # records
    path("api/records/sync", views.record_sync, name="record_sync"),
    path("api/records", views.record_submit, name="record_submit"),
    # stats / plan / notebook
    path("api/stats/summary", views.stats_summary, name="stats_summary"),
    path("api/plan/daily", views.plan_daily, name="plan_daily"),
    path("api/notebook/wrong", views.notebook_wrong, name="notebook_wrong"),
    path("api/notebook/stubborn", views.notebook_stubborn, name="notebook_stubborn"),
    path("api/notebook/summary", views.notebook_summary, name="notebook_summary"),
    # ai / agents
    path("api/ai/example", views.ai_example, name="ai_example"),
    path("api/agents/plan", views.agent_plan, name="agent_plan"),
    path("api/agents/tutor", views.agent_tutor, name="agent_tutor"),
    path("api/agents/train", views.agent_train, name="agent_train"),
    path("api/agents/analyze", views.agent_analyze, name="agent_analyze"),
]