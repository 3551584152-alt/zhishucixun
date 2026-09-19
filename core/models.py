# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class ApiToken(models.Model):
    key = models.CharField(max_length=64, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="api_tokens")
    created_at = models.DateTimeField(auto_now_add=True)


class Word(models.Model):
    word = models.CharField(max_length=64, unique=True)
    phonetic = models.CharField(max_length=128, blank=True, default="")
    pos = models.CharField(max_length=64, blank=True, default="")
    meaning = models.TextField(blank=True, default="")
    example = models.TextField(blank=True, default="")
    example_cn = models.TextField(blank=True, default="")
    synonyms = models.JSONField(default=list, blank=True)
    freq_read = models.IntegerField(default=0)
    freq_listen = models.IntegerField(default=0)
    freq_translate = models.IntegerField(default=0)
    freq_write = models.IntegerField(default=0)
    difficulty = models.IntegerField(default=2)
    mnemonic = models.TextField(blank=True, default="")
    collocations = models.JSONField(default=list, blank=True)
    confusables = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["word"]

    def freq_total(self):
        return self.freq_read + self.freq_listen + self.freq_translate + self.freq_write


class StudyRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="study_records")
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name="study_records")
    quality = models.IntegerField(default=3)
    review_type = models.CharField(max_length=16, default="learn")
    topic = models.CharField(max_length=16, blank=True, default="")
    is_correct = models.BooleanField(default=True)
    answered_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-answered_at"]


class ReviewState(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="review_states")
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name="review_states")
    stage = models.IntegerField(default=0)
    ease = models.FloatField(default=2.5)
    interval_minutes = models.IntegerField(default=0)
    next_review_at = models.DateTimeField(null=True, blank=True)
    lapses = models.IntegerField(default=0)
    wrong_count = models.IntegerField(default=0)
    correct_count = models.IntegerField(default=0)
    last_quality = models.IntegerField(default=-1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "word")

    @property
    def is_new(self):
        return self.stage <= 0 and self.correct_count == 0 and self.next_review_at is None

    @property
    def is_stubborn(self):
        return self.lapses >= 3 or self.wrong_count >= 3