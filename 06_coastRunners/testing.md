# Testing Guidelines

## What to Test

Tests should verify **behavior**, not structure. The type checker verifies structure.

| Test              | Don't Test           |
| ----------------- | -------------------- |
| Calculation logic | Constructors         |
| State transitions | Property access      |
| Side effects      | Protocol conformance |
| Error handling    | Field existence      |
| Edge cases        | Return types         |

### Protocol Conformance

Use a `TYPE_CHECKING` block to verify protocol conformance at type-check time:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mymodule.protocols import SomeProtocol

    _instance: SomeProtocol = MyImplementation(...)  # Type checker verifies this
```

This runs at type-check time, not runtime, and cannot drift out of sync.

### Tripwire Tests

The exception: **tripwire tests** that catch accidental removal of important
attributes (like `frozen=True` on dataclasses) are valuable:

```python
def test_is_immutable():
    """Tripwire: StateVector must be frozen."""
    state = StateVectorImpl(...)
    with pytest.raises(AttributeError):
        state.tick_id = 43  # type: ignore[misc]
```

## Test Style: DI + Fakes over Mocking

Prefer dependency injection with fake implementations over `mocker.patch()`.

| Approach       | When to Use      | Example             |
| -------------- | ---------------- | ------------------- |
| **DI + Fakes** | Default          | `FakeMqttPublisher` |
| **Patching**   | Third-party libs | `moto.mock_aws()`   |

### Pattern

1. Define a `Protocol` for the dependency
2. Create a reusable `Fake*` implementation
3. Inject via constructor
4. Only patch when dependency is unreachable or third-party

### Example

```python
# Protocol (in production code)
class MqttPublisherProtocol(Protocol):
    def publish(self, topic: str, event: dict, ...) -> None: ...

# Fake (in production code or testing_utils.py)
class FakeMqttPublisher:
    def __init__(self):
        self.sent_messages: list[Message] = []

    def publish(self, topic: str, event: dict, ...) -> None:
        self.sent_messages.append(Message(topic=topic, event=event, ...))

# Test
def test_publishes_to_correct_topic(fake_mqtt_publisher):
    publisher = MqttInferencePublisher(fake_mqtt_publisher, formatter)
    publisher.publish(record, plant_ref="adr", generation_ts=now)
    assert fake_mqtt_publisher.sent_messages[0].topic == "expected-topic"
```

### Reference Implementations

- `src/lib/adapters/mqtt/FakeMqttPublisher`
- `src/lib/modelling/utils/testing_utils.py`

## Test Structure

| Aspect    | Do                                 | Avoid                |
| --------- | ---------------------------------- | -------------------- |
| Structure | Flat functions                     | Test classes         |
| Setup     | Given-When-Then helpers            | Inline setup         |
| Names     | `test_when_condition_then_outcome` | `test_function_name` |
| Size      | ~100-200 lines per file            | 500+ line files      |

### Reference Tests

- `src/ci/artifacts/dynamo_test.py`
- `src/infra/google_auth_lambda/token_exchange_test.py`

## Test Levels

| Level           | What                   | Mock/Fake                  |
| --------------- | ---------------------- | -------------------------- |
| **Unit**        | Single component       | Fakes for collaborators    |
| **Integration** | Component interactions | Fakes for external systems |
| **E2E**         | Full system            | None                       |

## When Tests Are Hard to Write

If you need 3+ mocks to test something, the code is too coupled. Before writing tests:

1. Ask: "Is something making this hard?"
2. Check for dependency inversion violations
3. Refactor for DI first, then write tests

**Mocking is a workaround for tight coupling.**
If you need mocks, consider whether a design change would eliminate the need.

## Property-Based Testing with Hypothesis

For pure algorithmic components (controllers, filters, normalizers, calculators),
consider adding property-based tests using Hypothesis to verify mathematical
invariants.

### When to Use

- Roundtrip properties: `decode(encode(x)) == x`
- Boundary guarantees: output always within expected range
- Monotonicity: larger input → larger output (where applicable)
- Rate limiting: change never exceeds configured limit
- Invariants: properties that must hold for all valid inputs

### Example

```python
from hypothesis import given, strategies as st

@given(st.floats(min_value=0, max_value=100))
def test_normalize_always_bounded(value: float) -> None:
    """Property: normalized output always in [-1, +1] range."""
    result = normalizer.normalize(value)
    assert -1.0 <= result <= 1.0
```

### Benefits

- Tests mathematical invariants across wide input ranges
- Finds edge cases that example-based tests miss
- Hypothesis shrinks failures to minimal reproducing examples
- Provides stronger guarantees about component behavior

Property tests complement (don't replace) example-based tests. Use both.
