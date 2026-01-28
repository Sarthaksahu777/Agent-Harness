# EmoCore

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

EmoCore is a runtime governor that forces autonomous systems to halt when they stop making progress.

## What It Does

EmoCore sits between your agent loop and execution. It doesn't choose actions or inspect reasoning — it decides whether the system is still allowed to act.

```text
Agent/LLM → EmoCore (HALT/GO) → Action Execution
```

### Key Guarantees

- **Finite-time halting** under sustained non-progress
- **Deterministic behavior**: Same inputs = same outcome
- **Irreversible halting**: Once halted, stays halted
- **Model-agnostic**: Works with any agent architecture

### Failure Modes

| Condition | Result |
|:---|:---|
| Exploration > max | `SAFETY` halt |
| Risk > max | `OVERRISK` halt |
| Effort depleted | `EXHAUSTION` halt |
| Progress stalled | `STAGNATION` halt |
| Steps >= max | `EXTERNAL` halt |

## Usage

```python
from emocore import EmoCoreAgent, step, Signals

agent = EmoCoreAgent()

while True:
    result = step(agent, Signals(reward=0.0, novelty=0.0, urgency=0.1))
    
    if result.halted:
        print(f"Halted: {result.failure}")
        break
```

## Profiles

```python
from emocore import EmoCoreAgent, PROFILES, ProfileType

agent = EmoCoreAgent()  # Default: BALANCED
agent = EmoCoreAgent(PROFILES[ProfileType.CONSERVATIVE])  # Halts early
agent = EmoCoreAgent(PROFILES[ProfileType.AGGRESSIVE])    # Higher tolerance
```

## Integrations

Works with LangChain, AutoGen, CrewAI, and OpenAI SDK. See [`integrations/`](integrations/).

## License

MIT
