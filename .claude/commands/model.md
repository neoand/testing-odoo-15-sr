# Model Switch Command

Switch between different API providers and models for Claude interactions.

## Usage

```
/model [provider] [model]
```

## Available Providers

### z.ai (GLM Models)
- **glm-4.5-air** - Fast and efficient (default)
- **glm-4.6** - Most capable
- **glm-4.6** - Premium model

### minimax (MiniMax Models)
- **abab6.5-chat** - MiniMax chat model
- **abab6.5-chat** - Default MiniMax model

### direct (Anthropic Official)
- **claude-3-5-haiku-20241022** - Fast Anthropic model
- **claude-3-5-sonnet-20241022** - Balanced Anthropic model
- **claude-3-5-sonnet-20241022** - Premium Anthropic model

## Examples

```bash
/model z.ai                    # Switch to z.ai with default glm-4.6
/model z.ai glm-4.5-air       # Switch to z.ai with fast model
/model minimax                # Switch to MiniMax API
/model direct                 # Switch to direct Anthropic API
/model direct claude-3-5-sonnet-20241022  # Direct Anthropic with specific model
```

## Quick Switch

- `/model z` - Switch to z.ai
- `/model m` - Switch to MiniMax
- `/model d` - Switch to Direct Anthropic

## Status

To check current provider and model:
```
/model status
```

## Configuration

This command updates the `.claude/.env` file with the appropriate API configuration:
- `ANTHROPIC_AUTH_TOKEN`
- `ANTHROPIC_BASE_URL`
- `ANTHROPIC_API_URL`
- `ANTHROPIC_MODEL`
- Various model-specific settings

## Implementation Notes

- Automatically backs up current .env before switching
- Validates provider names and model compatibility
- Reloads environment variables after switching
- Maintains separate API keys for each provider