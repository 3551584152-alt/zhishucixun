# -*- coding: utf-8 -*-
"""Seed word bank: python manage.py seed_words"""
import io
import json
import os

from django.core.management.base import BaseCommand

from core.models import Word


class Command(BaseCommand):
    help = "导入内置 CET-4 示例词库"

    def handle(self, *args, **options):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "word_bank.json")
        with io.open(path, encoding="utf-8") as f:
            rows = json.load(f)
        created = 0
        for r in rows:
            _, made = Word.objects.update_or_create(
                word=r["word"],
                defaults={
                    "phonetic": r.get("phonetic", ""),
                    "pos": r.get("pos", ""),
                    "meaning": r.get("meaning", ""),
                    "example": r.get("example", ""),
                    "example_cn": r.get("example_cn", ""),
                    "synonyms": r.get("synonyms", []),
                    "freq_read": r.get("freq_read", 0),
                    "freq_listen": r.get("freq_listen", 0),
                    "freq_translate": r.get("freq_translate", 0),
                    "freq_write": r.get("freq_write", 0),
                    "difficulty": r.get("difficulty", 2),
                    "mnemonic": r.get("mnemonic", ""),
                    "collocations": r.get("collocations", []),
                    "confusables": r.get("confusables", []),
                },
            )
            if made:
                created += 1
        self.stdout.write("word bank ready: %d total, %d created" % (Word.objects.count(), created))