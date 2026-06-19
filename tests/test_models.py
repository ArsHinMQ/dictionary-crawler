import pytest
from pydantic import ValidationError

from dict_crawler.models.cambridge import (
    CambridgeCollocation,
    CambridgeDefinition,
    CambridgeDefinitionExample,
    CambridgeEntry,
    CambridgeExample,
    CambridgeSource,
    CambridgePage,
    CambridgePronunciation,
    CambridgeSection,
    CambridgeSectionPhrase,
    CambridgeSectionType,
    CambridgeSense,
    CambridgeVerbForm,
)
from dict_crawler.models.common import CEFRLevel


# --- CambridgeSectionType ---


def test_section_type_from_american():
    assert CambridgeSectionType.from_cambridge_text("American Dictionary") == CambridgeSectionType.American


def test_section_type_from_business():
    assert CambridgeSectionType.from_cambridge_text("Business English") == CambridgeSectionType.Business


def test_section_type_from_british_default():
    assert CambridgeSectionType.from_cambridge_text("English") == CambridgeSectionType.British
    assert CambridgeSectionType.from_cambridge_text("Unknown") == CambridgeSectionType.British


# --- CambridgeDefinitionExample ---


def test_definition_example_minimal():
    ex = CambridgeDefinitionExample(phrase=None, example="a test")
    assert ex.phrase is None
    assert ex.example == "a test"


def test_definition_example_full():
    ex = CambridgeDefinitionExample(phrase="in context", example="this is an example")
    assert ex.phrase == "in context"
    assert ex.example == "this is an example"


# --- CambridgeDefinition ---


def test_definition_minimal():
    d = CambridgeDefinition(definition="a thing", image_urls=None, examples=None)
    assert d.definition == "a thing"
    assert d.image_urls is None
    assert d.examples is None


def test_definition_with_examples():
    ex = CambridgeDefinitionExample(phrase=None, example="sample")
    d = CambridgeDefinition(
        definition="to run fast",
        image_urls=None,
        examples=[ex],
    )
    assert len(d.examples) == 1
    assert d.examples[0].example == "sample"


def test_definition_with_images():
    d = CambridgeDefinition(
        definition="a shape",
        image_urls=["https://example.com/img.png"],
        examples=None,
    )
    assert d.image_urls == ["https://example.com/img.png"]


# --- CambridgeSense ---


def test_sense_with_cefr():
    s = CambridgeSense(cefr=CEFRLevel.B2, definitions=[])
    assert s.cefr == CEFRLevel.B2
    assert s.definitions == []


def test_sense_without_cefr():
    s = CambridgeSense(cefr=None, definitions=[])
    assert s.cefr is None


# --- CambridgePronunciation ---


def test_pronunciation():
    p = CambridgePronunciation(
        pronunciation="/həˈləʊ/",
        audio_urls=["https://example.com/audio.mp3"],
        region="UK",
    )
    assert p.pronunciation == "/həˈləʊ/"
    assert len(p.audio_urls) == 1
    assert p.region == "UK"


# --- CambridgeVerbForm ---


def test_verb_form():
    vf = CambridgeVerbForm(form="running", name="present participle")
    assert vf.form == "running"
    assert vf.name == "present participle"


def test_verb_form_no_name():
    vf = CambridgeVerbForm(form="ran", name=None)
    assert vf.name is None


# --- CambridgeSectionPhrase ---


def test_section_phrase():
    sp = CambridgeSectionPhrase(headword="look after", definitions=[])
    assert sp.headword == "look after"
    assert sp.definitions == []


# --- CambridgeEntry ---


def test_entry_minimal():
    e = CambridgeEntry(
        headword="hello",
        part_of_speech="exclamation",
        pronunciations=None,
        verb_forms=None,
        senses=[],
        phrases=None,
        idioms=None,
        phrasal_verbs=None,
    )
    assert e.headword == "hello"
    assert e.part_of_speech == "exclamation"
    assert e.senses == []


def test_entry_full():
    e = CambridgeEntry(
        headword="run",
        part_of_speech="verb",
        pronunciations=[CambridgePronunciation(pronunciation="/rʌn/", audio_urls=[], region="UK")],
        verb_forms=[CambridgeVerbForm(form="ran", name="past simple")],
        senses=[CambridgeSense(cefr=CEFRLevel.A1, definitions=[])],
        phrases=[CambridgeSectionPhrase(headword="run after", definitions=[])],
        idioms=["run out of steam"],
        phrasal_verbs=["run away"],
    )
    assert e.pronunciations is not None
    assert len(e.pronunciations) == 1
    assert e.verb_forms is not None
    assert len(e.verb_forms) == 1
    assert e.idioms == ["run out of steam"]
    assert e.phrasal_verbs == ["run away"]


# --- CambridgeExample ---


def test_example_without_source():
    ex = CambridgeExample(example="Hello world", source=None)
    assert ex.example == "Hello world"
    assert ex.source is None


def test_example_with_source():
    src = CambridgeSource(from_="Cambridge Dictionary", link="https://example.com")
    ex = CambridgeExample(example="test", source=src)
    assert ex.source.from_ == "Cambridge Dictionary"


# --- CambridgeCollocation ---


def test_collocation():
    c = CambridgeCollocation(
        collocation="make a decision",
        example="We need to make a decision.",
        from_="Cambridge",
    )
    assert c.collocation == "make a decision"
    assert c.from_ == "Cambridge"


# --- CambridgePage ---


def test_page_minimal():
    p = CambridgePage(search_term="hello", sections=[], examples=None, collocations=None)
    assert p.search_term == "hello"
    assert p.sections == []
    assert p.examples is None
    assert p.collocations is None


def test_page_full():
    section = CambridgeSection(type=CambridgeSectionType.British, entries=[])
    example = CambridgeExample(example="test", source=None)
    collocation = CambridgeCollocation(collocation="colloc", example="ex", from_=None)
    p = CambridgePage(
        search_term="test",
        sections=[section],
        examples=[example],
        collocations=[collocation],
    )
    assert len(p.sections) == 1
    assert len(p.examples) == 1
    assert len(p.collocations) == 1
