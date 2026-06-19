from enum import Enum

from pydantic import BaseModel

from dictionary_crawler.models.common import CEFRLevel


class CambridgeSectionType(Enum):
    British = "british"
    American = "american"
    Business = "business"

    @classmethod
    def from_cambridge_text(cls, text: str):
        match text.lower():
            case "american dictionary":
                return CambridgeSectionType.American
            case "business english":
                return CambridgeSectionType.Business
            case _:
                return CambridgeSectionType.British
            
class CambridgeSource(BaseModel):
    # Where the example/collocation is from; e.g "Cambridge English Corpus"
    from_: str
    link: str | None


class CambridgeDefinitionExample(BaseModel):
    phrase: str | None
    example: str | None


class CambridgeDefinition(BaseModel):
    definition: str
    image_urls: list[str] | None
    examples: list[CambridgeDefinitionExample] | None


class CambridgeSense(BaseModel):
    cefr: CEFRLevel | None
    definitions: list[CambridgeDefinition]


class CambridgePronunciation(BaseModel):
    pronunciation: str
    audio_urls: list[str]
    region: str


class CambridgeVerbForm(BaseModel):
    form: str
    name: str | None


class CambridgeSectionPhrase(BaseModel):
    headword: str
    definitions: list[CambridgeDefinition]


class CambridgeEntry(BaseModel):
    headword: str
    part_of_speech: str
    pronunciations: list[CambridgePronunciation] | None
    verb_forms: list[CambridgeVerbForm] | None
    senses: list[CambridgeSense]
    phrases: list[CambridgeSectionPhrase] | None
    # Cambridge lists idioms and phrasal verbs as texts with a link to their own dictionary page, you can search each idiom/phrasal verb separately using the .crawl method again (recursive; maybe we can add an option to crawl every idiom and phrasal verb as well?)
    idioms: list[str] | None
    phrasal_verbs: list[str] | None


class CambridgeSection(BaseModel):
    type: CambridgeSectionType
    entries: list[CambridgeEntry]


class CambridgeExample(BaseModel):
    example: str
    source: CambridgeSource | None


class CambridgeCollocation(BaseModel):
    collocation: str
    example: str
    source: CambridgeSource | None


class CambridgePage(BaseModel):
    search_term: str
    sections: list[CambridgeSection]
    examples: list[CambridgeExample] | None
    collocations: list[CambridgeCollocation] | None
