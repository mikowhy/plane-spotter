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

Use modern Python 3.10+ syntax:

- `list[dict]` instead of `List[Dict]`
- `str | None` instead of `Optional[str]`
- `tuple[float, float]` instead of `Tuple[float, float]`