from dictionary_crawler.base import BaseCrawler
from dictionary_crawler.crawlers import CambridgeCrawler
from dictionary_crawler.exceptions import (
    DictionaryException,
    DictionaryFetchException,
    DictionaryParseException,
    DictionaryWordNotFoundException,
    CambridgeException,
    CambridgeFetchException,
    CambridgeParseException,
    CambridgeWordNotFoundException,
)
from dictionary_crawler.http import create_client
from dictionary_crawler.utils import generate_link
from dictionary_crawler.models import (
    CEFRLevel,
    CambridgeSectionType,
    CambridgeDefinitionExample,
    CambridgeDefinition,
    CambridgeSense,
    CambridgePronunciation,
    CambridgeVerbForm,
    CambridgeSectionPhrase,
    CambridgeEntry,
    CambridgeSection,
    CambridgeSource,
    CambridgeExample,
    CambridgeCollocation,
    CambridgePage,
)

__all__ = [
    "BaseCrawler",
    "CambridgeCrawler",
    "create_client",
    "generate_link",
    "DictionaryException",
    "DictionaryFetchException",
    "DictionaryParseException",
    "DictionaryWordNotFoundException",
    "CambridgeException",
    "CambridgeFetchException",
    "CambridgeParseException",
    "CambridgeWordNotFoundException",
    "CEFRLevel",
    "CambridgeSectionType",
    "CambridgeDefinitionExample",
    "CambridgeDefinition",
    "CambridgeSense",
    "CambridgePronunciation",
    "CambridgeVerbForm",
    "CambridgeSectionPhrase",
    "CambridgeEntry",
    "CambridgeSection",
    "CambridgeSource",
    "CambridgeExample",
    "CambridgeCollocation",
    "CambridgePage",
]
