# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-LLM Agent System: An agent that queries multiple LLMs (OpenAI GPT, Google Gemini, Anthropic Claude) in parallel, performs comprehensive web/arXiv searches, and synthesizes unified responses from diverse perspectives.

## Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Or using venv
./venv/bin/pip install -r requirements.txt

# Configure API keys (required)
cp .env.example .env
# Edit .env with your API keys
```

### Running the Agent
```bash
# Main CLI
python -m multi_llm_agent.main "your question here"

# Single question test
./venv/bin/python test_single_question.py

# Run all test questions
./venv/bin/python test_questions.py
```

### Testing Individual Components
```bash
# Test specific LLM provider
python -c "from multi_llm_agent.llm_providers import OpenAIProvider; ..."

# Test search functionality
python -c "from multi_llm_agent.search_agent import ComprehensiveSearchAgent; ..."
```

## Architecture

### Core Processing Flow

1. **ComprehensiveSearchAgent** (`search_agent.py`)
   - Executes multiple search iterations with query diversification
   - Deduplicates results by URL
   - Supports parallel searches across arXiv and web sources
   - Configurable via `SearchConfig` (max_iterations, results_per_iteration)

2. **MultiLLMOrchestrator** (`orchestrator.py`)
   - Manages parallel LLM queries (or sequential if `enable_parallel_processing=False`)
   - Creates provider instances from `LLMProviderConfig`
   - Handles provider failures gracefully with error responses
   - Returns `Dict[str, LLMResponse]` with provider names as keys

3. **ResponseAggregator** (`aggregator.py`)
   - Analyzes differences between LLM responses (length, time, tokens)
   - Uses an LLM to synthesize unified response from multiple answers
   - Creates comparison tables
   - Falls back to simple concatenation if synthesis fails

4. **MultiLLMAgent** (`main.py`)
   - Entry point orchestrating the full pipeline
   - Manages `OutputManager` for saving results to `output/` directory
   - Handles async/sync execution via `query()` and `query_sync()`
   - Uses `TimeTracker` for performance monitoring

### LLM Provider Architecture

All providers inherit from `BaseLLMProvider` (`llm_providers/base.py`):
- Must implement `generate()` (async) and `generate_sync()`
- Must implement `provider_name` property
- Return `LLMResponse` dataclass with provider, model, content, tokens, response_time

Providers:
- `OpenAIProvider`: OpenAI GPT models
- `GeminiProvider`: Google Gemini models
- `AnthropicProvider`: Anthropic Claude models

### Searcher Architecture

All searchers inherit from `BaseSearcher` (`searchers/base.py`):
- Must implement `search()` (async) and `search_sync()`
- Return `List[SearchResult]` with title, url, snippet

Searchers:
- `ArxivSearcher`: Academic papers from arXiv
- `WebSearcher`: Web search via DuckDuckGo

### Configuration System

`Config.from_env()` loads from environment variables:
- **LLM Providers**: API keys, models, temperature, max_tokens for each provider
- **Search**: max_iterations (default 3), results_per_iteration (default 10)
- **Aggregation**:
  - aggregation_model (default "gpt-4"): Model used for synthesis
  - aggregation_max_tokens (default 4000): Max output tokens for synthesis
  - aggregation_temperature (default 0.7): Temperature for synthesis
  - enable_parallel_processing (default True)
- **Timeouts**:
  - llm_timeout (60s): Timeout for regular LLM queries
  - aggregation_timeout (180s): Timeout for synthesis (longer for complex prompts)
  - search_timeout (30s): Timeout for search operations
- **Debug**: verbose (default True), debug (default False)

See `.env.example` for all configuration options.

### Output Management

`OutputManager` (`output_manager.py`):
- Creates timestamped directories: `output/YYYYMMDD_HHMMSS/`
- Saves JSON results: `result.json`
- Saves markdown summaries: `result.md`
- Saves synthesized responses: `synthesis.md`
- Maintains log file: `process.log`

## Key Implementation Details

### Error Handling
- LLM provider failures return `LLMResponse` with `metadata["error"]`
- Search failures are caught and logged but don't stop execution
- Missing API keys skip that provider with warning

### Query Diversification Strategy
`ComprehensiveSearchAgent._diversify_query()` appends to queries:
- Iteration 1: "overview"
- Iteration 2: "tutorial"
- Iteration 3: "best practices"
- Iteration 4+: cycles through "examples", "comparison", "latest", etc.

### Parallel Execution
When `enable_parallel_processing=True`:
- Uses `asyncio.gather()` to query all LLMs simultaneously
- Catches exceptions per-provider using `return_exceptions=True`

### Synthesis Prompt
`ResponseAggregator._create_synthesis_prompt()` asks the aggregation LLM to:
1. Identify commonalities and differences
2. Flag contradictions
3. Prioritize reliable information
4. Generate comprehensive unified answer
5. Add necessary caveats

### Time Tracking
`TimeTracker` uses context manager:
```python
with time_tracker.measure("task_name"):
    # code to measure
```
Tracks total time and individual task durations.

## Model Configuration Notes

See `docs/LLM_MODELS_GUIDE.md` for:
- Current model names (as of Dec 2025)
- Deprecated/legacy models
- Recommended settings by use case
- API parameter changes (e.g., `max_tokens` → `max_completion_tokens`)

**Important**: Model names include date suffixes (e.g., `claude-opus-4.5-20251101`). Verify current model names in official docs before changing config.

## Common Patterns

### Adding a New LLM Provider
1. Create `multi_llm_agent/llm_providers/new_provider.py`
2. Inherit from `BaseLLMProvider`
3. Implement `generate()`, `generate_sync()`, and `provider_name`
4. Update `orchestrator.py._create_provider()` to handle new provider name
5. Add config to `Config.from_env()` in `config.py`
6. Add environment variables to `.env.example`

### Adding a New Searcher
1. Create `multi_llm_agent/searchers/new_searcher.py`
2. Inherit from `BaseSearcher`
3. Implement `search()` and `search_sync()`
4. Update `search_agent.py._initialize_searchers()` to instantiate
5. Add enable flag to `SearchConfig`

### Debugging a Query
Enable verbose mode:
```python
agent = MultiLLMAgent()
agent.config.verbose = True
result = agent.query_sync("question", use_search=True, synthesize=True)
```
Or set `VERBOSE=true` in `.env`.

## Dependencies
- `openai>=1.12.0` - OpenAI API
- `google-genai>=0.1.0` - Google Gemini API
- `anthropic>=0.18.0` - Anthropic Claude API
- `arxiv>=2.1.0` - arXiv paper search
- `aiohttp>=3.9.0` - Async HTTP client
- `beautifulsoup4>=4.12.0` - HTML parsing for web search
- `python-dotenv>=1.0.0` - Environment variable loading
- `tenacity>=8.2.0` - Retry logic
