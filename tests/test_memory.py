"""Tests for Long-Term Memory Store."""

# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀


import os
import tempfile
from memory.long_term import LongTermMemory


def test_memory_remember_and_recall():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        temp_path = tf.name

    try:
        mem = LongTermMemory(file_path=temp_path)
        rem = mem.remember("favorite_artist", "Queen")
        assert rem["success"] is True

        rec = mem.recall("favorite_artist")
        assert rec["found"] is True
        assert rec["value"] == "Queen"

        # Case-insensitivity check
        rec_upper = mem.recall("FAVORITE_ARTIST")
        assert rec_upper["found"] is True
        assert rec_upper["value"] == "Queen"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_memory_forget():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        temp_path = tf.name

    try:
        mem = LongTermMemory(file_path=temp_path)
        mem.remember("temp_code", "1234")
        assert mem.recall("temp_code")["found"] is True

        f_res = mem.forget("temp_code")
        assert f_res["success"] is True
        assert mem.recall("temp_code")["found"] is False
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_memory_persistence():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        temp_path = tf.name

    try:
        mem1 = LongTermMemory(file_path=temp_path)
        mem1.remember("boss_name", "Aaditya")

        # Load new instance pointing to same file
        mem2 = LongTermMemory(file_path=temp_path)
        rec = mem2.recall("boss_name")
        assert rec["found"] is True
        assert rec["value"] == "Aaditya"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
