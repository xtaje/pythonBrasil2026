"""Unit tests for the domain logic in fizzbuzz.core.

This is the only module with real business rules in it, so it carries the
heaviest test weight in the suite -- everything else in this project is I/O
plumbing around a five-line function, and gets tested accordingly (see the
adapter test files for where mocking at the architectural boundary takes
over).
"""

from __future__ import annotations

import pytest

from fizzbuzz.core import DEFAULT_RULES, Rule, fizzbuzz, fizzbuzz_range


class TestFizzBuzz:
    @pytest.mark.parametrize(
        ("n", "expected"),
        [
            (1, "1"),
            (2, "2"),
            (3, "Fizz"),
            (4, "4"),
            (5, "Buzz"),
            (6, "Fizz"),
            (9, "Fizz"),
            (10, "Buzz"),
            (15, "FizzBuzz"),
            (30, "FizzBuzz"),
            (100, "Buzz"),
        ],
    )
    def test_known_values(self, n: int, expected: str) -> None:
        assert fizzbuzz(n) == expected

    def test_rejects_zero(self) -> None:
        with pytest.raises(ValueError, match="positive integer"):
            fizzbuzz(0)

    def test_rejects_negative(self) -> None:
        with pytest.raises(ValueError, match="positive integer"):
            fizzbuzz(-5)

    def test_custom_rules_replace_defaults_entirely(self) -> None:
        rules = (Rule(2, "Even"),)
        assert fizzbuzz(4, rules) == "Even"
        assert fizzbuzz(3, rules) == "3"  # no rule matches 3 once defaults are gone

    def test_rule_order_controls_concatenation_order(self) -> None:
        rules = (Rule(5, "Buzz"), Rule(3, "Fizz"))
        assert fizzbuzz(15, rules) == "BuzzFizz"

    def test_default_rules_is_an_immutable_tuple(self) -> None:
        # Regression guard: a mutable default here would let one caller's
        # `DEFAULT_RULES.append(...)` corrupt behaviour for every other
        # caller sharing the same default. Nothing should be able to.
        assert isinstance(DEFAULT_RULES, tuple)
        with pytest.raises(AttributeError):
            DEFAULT_RULES.append(Rule(7, "Whizz"))  # type: ignore[attr-defined]


class TestRule:
    def test_rejects_non_positive_divisor(self) -> None:
        with pytest.raises(ValueError, match="divisor"):
            Rule(0, "Fizz")
        with pytest.raises(ValueError, match="divisor"):
            Rule(-3, "Fizz")

    def test_rejects_empty_word(self) -> None:
        with pytest.raises(ValueError, match="word"):
            Rule(3, "")

    def test_is_frozen(self) -> None:
        rule = Rule(3, "Fizz")
        with pytest.raises(AttributeError):
            rule.divisor = 5  # type: ignore[misc]


class TestFizzBuzzRange:
    def test_produces_the_classic_sequence_for_1_to_15(self) -> None:
        assert list(fizzbuzz_range(1, 15)) == [
            "1",
            "2",
            "Fizz",
            "4",
            "Buzz",
            "Fizz",
            "7",
            "8",
            "Fizz",
            "Buzz",
            "11",
            "Fizz",
            "13",
            "14",
            "FizzBuzz",
        ]

    def test_single_element_range(self) -> None:
        assert list(fizzbuzz_range(5, 5)) == ["Buzz"]

    def test_rejects_start_after_end(self) -> None:
        with pytest.raises(ValueError, match="must be <="):
            fizzbuzz_range(10, 1)

    def test_validation_is_eager_not_deferred_to_iteration(self) -> None:
        # See the comment on fizzbuzz_range itself: this is specifically
        # guarding against the classic "it's a generator function so the
        # guard clause never actually runs until someone calls next()"
        # mistake. Calling this must raise before any iteration happens.
        with pytest.raises(ValueError):
            iterator = fizzbuzz_range(10, 1)
            # If this line were ever reached, the bug is back: the
            # exception above should already have fired on the call itself.
            next(iterator)  # pragma: no cover

    def test_returns_a_lazy_iterator_not_a_materialized_list(self) -> None:
        result = fizzbuzz_range(1, 1_000_000)
        assert hasattr(result, "__next__")
        assert not isinstance(result, list)
