# Coding Conventions

## Type Hints

Always use type hints for:

- **Function arguments** -- every parameter must have a type annotation
- **Return types** -- every function must declare its return type

```python
# Good
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    ...

async def get_history(limit: int = 50, offset: int = 0) -> list[dict]:
    ...

# Bad -- missing types
def haversine(lat1, lon1, lat2, lon2):
    ...
```

## Imports

All imports must be at the top of the file. No inline or mid-function imports.

```python
# Good
import planespotter.database as db_mod
from planespotter.database import get_history

def use_temp_db():
    db_mod.do_something()

# Bad -- import inside function
def use_temp_db():
    import planespotter.database as db_mod
    db_mod.do_something()
```

Use absolute imports (`from planespotter.module`) instead of relative imports (`from .module`).

## Function Calls

Always use named arguments (keyword arguments) when calling functions.

If a call has more than 1 argument, put each argument on its own line with a trailing comma:

```python
# Good
await log_flight(
    icao24="abc123",
    callsign="TEST1",
    origin_country="Poland",
    altitude=300.0,
    distance=2.5,
    on_approach=True,
)

# Bad -- positional arguments
await log_flight("abc123", "TEST1", "Poland", 300.0, 2.5, True)

# Bad -- multiple arguments on one line
await log_flight(icao24="abc123", callsign="TEST1", origin_country="Poland")
```

Single-argument calls can stay on one line: `get_history(limit=10)`

## Modern Syntax

Use modern Python 3.10+ syntax:

- `list[dict]` instead of `List[Dict]`
- `str | None` instead of `Optional[str]`
- `tuple[float, float]` instead of `Tuple[float, float]`