# Claude Code Model Configuration Reference

Source: https://code.claude.com/docs/en/model-config

## Model Aliases

| Alias | Behavior |
|-------|----------|
| `default` | Recommended model based on your account type |
| `sonnet` | Latest Sonnet model (currently Sonnet 4.6) for daily coding tasks |
| `opus` | Latest Opus model (currently Opus 4.7) for complex reasoning tasks |
| `haiku` | Fast and efficient Haiku model for simple tasks |
| `sonnet[1m]` | Sonnet with 1 million token context window for long sessions |
| `opusplan` | Uses `opus` in plan mode, switches to `sonnet` for execution |

Aliases always point to the latest version. To pin a specific version, use full model name (e.g., `claude-opus-4-6`).

## Setting Your Model

Priority order (highest to lowest):

1. **During session**: `/model <alias|name>`
2. **At startup**: `claude --model <alias|name>`
3. **Environment variable**: `ANTHROPIC_MODEL=<alias|name>`
4. **Settings file**: `"model": "<alias|name>"` in settings.json

## Settings File Example

```json
{
    "permissions": {
        "allow": [...]
    },
    "model": "opusplan"
}
```

## Special Model Behaviors

### `default` model behavior
- **Max and Team Premium**: defaults to Opus 4.6
- **Pro and Team Standard**: defaults to Sonnet 4.6
- **Enterprise**: Opus 4.6 available but not default

Claude Code may fall back to Sonnet if you hit usage threshold with Opus.

### `opusplan` model behavior
- **Plan mode** (`/plan`): Uses `opus` for complex reasoning and architecture
- **Execution mode**: Uses `sonnet` for code generation and implementation

Best of both worlds: Opus reasoning for planning, Sonnet efficiency for execution.

### Effort Levels (Adaptive Reasoning)
Controls thinking depth based on task complexity. Available: `low`, `medium`, `high`.

**Setting effort:**
- In `/model`: use arrow keys to adjust effort slider
- Environment: `CLAUDE_CODE_EFFORT_LEVEL=low|medium|high`
- Settings: `"effortLevel": "medium"`

Opus 4.6 defaults to medium effort for Max and Team subscribers.

To disable adaptive reasoning: `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1`

### Extended Context (1M tokens)
Available with `sonnet[1m]` or by appending `[1m]` to model names.

Standard rates until 200K tokens, then long-context pricing applies.

To disable: `CLAUDE_CODE_DISABLE_1M_CONTEXT=1`

## Environment Variables

### Model Alias Overrides
| Variable | Description |
|----------|-------------|
| `ANTHROPIC_MODEL` | Set default model alias or name |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Model for `opus` and `opusplan` plan mode |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Model for `sonnet` and `opusplan` execution |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Model for `haiku` and background tasks |
| `CLAUDE_CODE_SUBAGENT_MODEL` | Model for subagents |

### Other Settings
| Variable | Description |
|----------|-------------|
| `CLAUDE_CODE_EFFORT_LEVEL` | `low`, `medium`, or `high` |
| `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING` | Set to `1` to use fixed thinking budget |
| `CLAUDE_CODE_DISABLE_1M_CONTEXT` | Set to `1` to disable 1M context |
| `DISABLE_PROMPT_CACHING` | Set to `1` to disable caching for all models |
| `DISABLE_PROMPT_CACHING_HAIKU` | Disable caching for Haiku only |
| `DISABLE_PROMPT_CACHING_SONNET` | Disable caching for Sonnet only |
| `DISABLE_PROMPT_CACHING_OPUS` | Disable caching for Opus only |

## Enterprise: Restrict Model Selection

Admins can limit available models:

```json
{
  "model": "sonnet",
  "availableModels": ["sonnet", "haiku"]
}
```

## Check Current Model

- Use `/status` to see current model and account info
- Configure status line to show model
