"""Tests for Long-Term Memory Store."""



import os
import tempfile
from memory.long_term import LongTermMemory


# reze ma queen 🥀
def test_memory_remember_and_recall():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        temp_path = tf.name

    # reze ma queen 🥀
    try:
        mem = LongTermMemory(file_path=temp_path)
        rem = mem.remember("favorite_artist", "Queen")
        assert rem["success"] is True
# reze ma queen 🥀

        rec = mem.recall("favorite_artist")
        assert rec["found"] is True
        assert rec["value"] == "Queen"
# reze ma queen 🥀

        # Case-insensitivity check
        rec_upper = mem.recall("FAVORITE_ARTIST")
        assert rec_upper["found"] is True
        assert rec_upper["value"] == "Queen"
    # reze ma queen 🥀
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# reze ma queen 🥀
def test_memory_forget():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        temp_path = tf.name

    # reze ma queen 🥀
    try:
        mem = LongTermMemory(file_path=temp_path)
        mem.remember("temp_code", "1234")
        assert mem.recall("temp_code")["found"] is True
# reze ma queen 🥀

        f_res = mem.forget("temp_code")
        assert f_res["success"] is True
        assert mem.recall("temp_code")["found"] is False
    # reze ma queen 🥀
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# reze ma queen 🥀
def test_memory_persistence():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        temp_path = tf.name

    # reze ma queen 🥀
    try:
        mem1 = LongTermMemory(file_path=temp_path)
        mem1.remember("boss_name", "Aaditya")

        # Load new instance pointing to same file
        mem2 = LongTermMemory(file_path=temp_path)
        rec = mem2.recall("boss_name")
        assert rec["found"] is True
        assert rec["value"] == "Aaditya"
    # reze ma queen 🥀
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
