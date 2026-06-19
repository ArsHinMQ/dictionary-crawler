# 🦄 Dictionary Crawler

A Python package for crawling dictionary websites. Currently supports Cambridge Dictionary.

## Installation

```bash
pip install dictionary-crawler
```

Or install from source:

```bash
git clone https://github.com/arshinmq/dictionary-crawler.git
cd dictionary-crawler
pip install -e .
```

## Features

- Async HTTP client for non-blocking requests
- Parse Cambridge Dictionary pages
- Extract:
  - Headwords and parts of speech
  - Pronunciations (IPA + audio URLs)
  - Definitions with CEFR levels
  - Examples and sources
  - Phrases, idioms, and phrasal verbs
  - Collocations
  - Verb forms
- Structured Pydantic models for type-safe data access
- JSON serialization support

## Quick Start

```python
import asyncio
from dictionary_crawler import CambridgeCrawler

async def main():
    async with CambridgeCrawler() as crawler:
        page = await crawler.crawl("run")
        
        print(f"Search term: {page.search_term}")
        
        for section in page.sections:
            for entry in section.entries:
                print(f"\n{entry.headword} ({entry.part_of_speech})")
                
                if entry.pronunciations:
                    for p in entry.pronunciations:
                        print(f"  [{p.region}] {p.pronunciation}")
                
                for sense in entry.senses:
                    for defn in sense.definitions:
                        print(f"  - {defn.definition}")
                        if defn.examples:
                            for ex in defn.examples:
                                if ex.example:
                                    print(f"    e.g. {ex.example}")

asyncio.run(main())
```

## API Reference

### CambridgeCrawler

The main crawler class for Cambridge Dictionary.

```python
from dictionary_crawler import CambridgeCrawler

async with CambridgeCrawler() as crawler:
    page = await crawler.crawl(word: str) -> CambridgePage
```

#### Parameters

- `client` (optional): Custom `httpx.AsyncClient` instance

### Data Models

#### CambridgePage

The root model containing all parsed data:

| Field | Type | Description |
|-------|------|-------------|
| `search_term` | `str` | The word that was searched |
| `sections` | `list[CambridgeSection]` | Dictionary sections (British, American, Business) |
| `examples` | `list[CambridgeExample] \| None` | Example sentences |
| `collocations` | `list[CambridgeCollocation] \| None` | Collocations |

#### CambridgeSection

| Field | Type | Description |
|-------|------|-------------|
| `type` | `CambridgeSectionType` | British, American, or Business |
| `entries` | `list[CambridgeEntry]` | Dictionary entries |

#### CambridgeEntry

| Field | Type | Description |
|-------|------|-------------|
| `headword` | `str` | The word/phrase |
| `part_of_speech` | `str` | noun, verb, adjective, etc. |
| `pronunciations` | `list[CambridgePronunciation] \| None` | Pronunciations |
| `senses` | `list[CambridgeSense]` | Word senses with definitions |
| `phrases` | `list[CambridgeSectionPhrase] \| None` | Related phrases |
| `idioms` | `list[str] \| None` | Related idioms |
| `phrasal_verbs` | `list[str] \| None` | Related phrasal verbs |
| `verb_forms` | `list[CambridgeVerbForm] \| None` | Verb conjugations |

#### CambridgePronunciation

| Field | Type | Description |
|-------|------|-------------|
| `pronunciation` | `str` | IPA transcription |
| `audio_urls` | `list[str]` | Audio file URLs |
| `region` | `str` | e.g., "UK", "US" |

#### CambridgeSense

| Field | Type | Description |
|-------|------|-------------|
| `cefr` | `CEFRLevel \| None` | CEFR level (A1-C2) |
| `definitions` | `list[CambridgeDefinition]` | Definitions |

#### CambridgeDefinition

| Field | Type | Description |
|-------|------|-------------|
| `definition` | `str` | The definition text |
| `examples` | `list[CambridgeDefinitionExample] \| None` | Example sentences |
| `image_urls` | `list[str] \| None` | Illustration URLs |

#### CEFRLevel

Enum with values: `A1`, `A2`, `B1`, `B2`, `C1`, `C2`

### Exceptions

| Exception | Description |
|-----------|-------------|
| `DictionaryException` | Base exception |
| `DictionaryFetchException` | HTTP request failed |
| `DictionaryWordNotFoundException` | Word not in dictionary |
| `DictionaryParseException` | Failed to parse page |
| `CambridgeException` | Cambridge-specific base |
| `CambridgeFetchException` | Cambridge fetch error |
| `CambridgeWordNotFoundException` | Word not in Cambridge |
| `CambridgeParseException` | Cambridge parse error |

## JSON Export

Models can be serialized to JSON:

```python
page = await crawler.crawl("example")
json_data = page.model_dump_json(indent=2, ensure_ascii=False)
print(json_data)
```

## Development

### Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Project Structure

```
dictionary-crawler/
├── src/
│   └── dictionary_crawler/
│       ├── __init__.py
│       ├── base.py          # BaseCrawler ABC
│       ├── http.py          # HTTP client setup
│       ├── utils.py         # URL utilities
│       ├── exceptions.py    # Custom exceptions
│       ├── crawlers/
│       │   └── cambridge.py # Cambridge parser
│       └── models/
│           ├── common.py    # Shared models (CEFRLevel)
│           └── cambridge.py # Cambridge data models
└── tests/
```

## Roadmap (Future)
- Add Oxford Dictionary support
- Support for additional dictionaries (Merriam-Webster, Collins, etc.)
- Multi-language support (Spanish, French, German, etc.)

## License

MIT
