#!/usr/bin/env python3
"""Test suite for credit card validator."""

from __future__ import annotations

import unittest

from credit_card_validator import (
    CARD_PATTERNS,
    detect_card_type,
    passes_luhn,
    validate_card,
    validate_expiration,
)


class TestLuhn(unittest.TestCase):
    def test_valid_numbers(self) -> None:
        numbers = [
            "4111111111111111",  # Visa
            "4012888888881881",  # Visa
            "5555555555554444",  # MasterCard
            "378282246310005",   # Amex
        ]
        for number in numbers:
            with self.subTest(number=number):
                self.assertTrue(passes_luhn(number))

    def test_invalid_numbers(self) -> None:
        numbers = [
            "4111111111111112",
            "5555555555554440",
            "378282246310006",
        ]
        for number in numbers:
            with self.subTest(number=number):
                self.assertFalse(passes_luhn(number))


class TestCardType(unittest.TestCase):
    def test_detect_visa(self) -> None:
        self.assertEqual(detect_card_type("4111111111111111"), "visa")

    def test_detect_mastercard(self) -> None:
        self.assertEqual(detect_card_type("5555555555554444"), "mastercard")

    def test_detect_amex(self) -> None:
        self.assertEqual(detect_card_type("378282246310005"), "amex")

    def test_unknown_card(self) -> None:
        self.assertIsNone(detect_card_type("1234567890123456"))


class TestExpiration(unittest.TestCase):
    def test_valid_future_date(self) -> None:
        self.assertTrue(validate_expiration("12/2099"))

    def test_invalid_format(self) -> None:
        self.assertFalse(validate_expiration("13/25"))

    def test_past_date(self) -> None:
        self.assertFalse(validate_expiration("01/20"))


class TestValidateCard(unittest.TestCase):
    def test_full_validation_success(self) -> None:
        result = validate_card("4111 1111 1111 1111", "12/2099")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.card_type, "visa")

    def test_full_validation_failure(self) -> None:
        result = validate_card("4111 1111 1111 1112", "12/2099")
        self.assertFalse(result.is_valid)
        self.assertIn("Failed Luhn", result.message)


if __name__ == "__main__":
    unittest.main()
