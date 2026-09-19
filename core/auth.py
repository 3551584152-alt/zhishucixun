# -*- coding: utf-8 -*-
"""极简 Token 鉴权（无第三方依赖）。"""
import functools
import secrets

from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import ApiToken


def make_token(user):
    key = secrets.token_hex(24)
    ApiToken.objects.create(key=key, user=user)
    return key


def user_payload(user):
    return {
        "id": user.id,
        "username": user.username,
        "nickname": getattr(user, "nickname", "") or user.username,
        "first_name": user.first_name or "",
    }


def get_user_from_request(request):
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        key = header[7:].strip()
        try:
            t = ApiToken.objects.select_related("user").get(key=key)
            return t.user
        except ApiToken.DoesNotExist:
            return None
    return None


def login_required(view):
    @functools.wraps(view)
    @csrf_exempt
    def wrapper(request, *args, **kwargs):
        user = get_user_from_request(request)
        if user is None:
            return JsonResponse({"detail": "登录已失效，请重新登录"}, status=401)
        return view(request, user, *args, **kwargs)
    return wrapper


def do_login(username, password):
    user = authenticate(username=username, password=password)
    return user


def ensure_nickname(user):
    """注册时把昵称写入 first_name（无需自建用户模型）。"""
    return user