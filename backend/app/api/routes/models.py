"""Models API routes."""
from fastapi import APIRouter

router = APIRouter()


# Model configurations with pricing
MODELS = [
    # OpenAI Models
    {
        "id": "gpt-4-turbo-preview",
        "name": "GPT-4 Turbo",
        "provider": "openai",
        "input_cost": 10.00,
        "output_cost": 30.00,
        "category": "OpenAI GPT-4"
    },
    {
        "id": "gpt-4",
        "name": "GPT-4",
        "provider": "openai",
        "input_cost": 30.00,
        "output_cost": 60.00,
        "category": "OpenAI GPT-4"
    },
    {
        "id": "gpt-3.5-turbo",
        "name": "GPT-3.5 Turbo",
        "provider": "openai",
        "input_cost": 0.50,
        "output_cost": 1.50,
        "category": "OpenAI GPT-3.5"
    },
    # Anthropic Claude 4.5 (Latest)
    {
        "id": "claude-opus-4-5-20251101",
        "name": "Claude Opus 4.5",
        "provider": "anthropic",
        "input_cost": 15.00,
        "output_cost": 75.00,
        "category": "Claude 4.5 (Latest)"
    },
    {
        "id": "claude-sonnet-4-5-20250929",
        "name": "Claude Sonnet 4.5",
        "provider": "anthropic",
        "input_cost": 3.00,
        "output_cost": 15.00,
        "category": "Claude 4.5 (Latest)"
    },
    {
        "id": "claude-haiku-4-5-20251001",
        "name": "Claude Haiku 4.5",
        "provider": "anthropic",
        "input_cost": 0.80,
        "output_cost": 4.00,
        "category": "Claude 4.5 (Latest)"
    },
    # Anthropic Claude 4
    {
        "id": "claude-opus-4-1-20250805",
        "name": "Claude Opus 4.1",
        "provider": "anthropic",
        "input_cost": 15.00,
        "output_cost": 75.00,
        "category": "Claude 4"
    },
    {
        "id": "claude-opus-4-20250514",
        "name": "Claude Opus 4",
        "provider": "anthropic",
        "input_cost": 15.00,
        "output_cost": 75.00,
        "category": "Claude 4"
    },
    {
        "id": "claude-sonnet-4-20250514",
        "name": "Claude Sonnet 4",
        "provider": "anthropic",
        "input_cost": 3.00,
        "output_cost": 15.00,
        "category": "Claude 4"
    },
    # Anthropic Claude 3.7 and 3.5
    {
        "id": "claude-3-7-sonnet-20250219",
        "name": "Claude 3.7 Sonnet",
        "provider": "anthropic",
        "input_cost": 3.00,
        "output_cost": 15.00,
        "category": "Claude 3.7 / 3.5"
    },
    {
        "id": "claude-3-5-haiku-20241022",
        "name": "Claude 3.5 Haiku",
        "provider": "anthropic",
        "input_cost": 0.80,
        "output_cost": 4.00,
        "category": "Claude 3.7 / 3.5"
    },
    # Anthropic Claude 3 (Legacy)
    {
        "id": "claude-3-opus-20240229",
        "name": "Claude 3 Opus",
        "provider": "anthropic",
        "input_cost": 15.00,
        "output_cost": 75.00,
        "category": "Claude 3 (Legacy)"
    },
    {
        "id": "claude-3-haiku-20240307",
        "name": "Claude 3 Haiku",
        "provider": "anthropic",
        "input_cost": 0.25,
        "output_cost": 1.25,
        "category": "Claude 3 (Legacy)"
    },
]


@router.get("/models")
async def list_models():
    """Get available LLM models with pricing."""
    return {
        "models": MODELS,
        "default_models": {
            "openai": "gpt-3.5-turbo",
            "anthropic": "claude-sonnet-4-5-20250929"
        }
    }
