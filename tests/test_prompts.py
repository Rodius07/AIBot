import unittest
import os

os.environ.setdefault("tg_token", "123:test")
os.environ.setdefault("openaitoken", "sk-test")
from aibot.prompts import build_messages


class PromptHistoryTests(unittest.TestCase):
    def test_history_is_included_in_system_prompt(self):
        messages = build_messages("пользователь: привет\nмайя: я рядом", "как дела?")

        self.assertEqual(messages[-1], {"role": "user", "content": "как дела?"})
        self.assertIn("История диалога:", messages[0]["content"])
        self.assertIn("пользователь: привет", messages[0]["content"])
        self.assertIn("майя: я рядом", messages[0]["content"])

    def test_empty_history_is_explicit(self):
        messages = build_messages("", "привет")

        self.assertIn("Истории диалога пока нет.", messages[0]["content"])


if __name__ == "__main__":
    unittest.main()
