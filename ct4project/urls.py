"""
URL configuration for ct4project.

- /admin/   : Django 后端管理后台 (simpleui)
- /api/*    : JSON API
- /         : Vue 前端 (SPA，由 Django 托管 frontend/dist)
"""
from pathlib import Path

from django.contrib import admin
from django.http import FileResponse, JsonResponse
from django.urls import include, path, re_path
from django.views.static import serve

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"


def spa_index(request):
    f = FRONTEND_DIST / "index.html"
    if f.exists():
        return FileResponse(f.open("rb"), content_type="text/html")
    return JsonResponse({"detail": "前端未构建，请先在 frontend 目录运行 npm run build"}, status=404)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    # Vue 构建产物静态资源
    re_path(r"^assets/(?P<path>.*)$", serve, {"document_root": str(FRONTEND_DIST / "assets")}),
    # SPA 前端路由回退（排除 api / admin / assets / static）
    re_path(r"^(?!api/?|admin/?|assets/?|static/?).*$", spa_index, name="spa_index"),
]