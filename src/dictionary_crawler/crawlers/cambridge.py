import logging

import httpx
from bs4 import BeautifulSoup, Tag

from dictionary_crawler.base import BaseCrawler
from dictionary_crawler.exceptions import (
    CambridgeException,
    CambridgeFetchException,
    CambridgeParseException,
    CambridgeWordNotFoundException,
)
from dictionary_crawler.models.cambridge import (
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
from dictionary_crawler.models.common import CEFRLevel
from dictionary_crawler.utils import generate_link

logger = logging.getLogger(__name__)


class CambridgeCrawler(BaseCrawler):
    _base_url: str = "https://dictionary.cambridge.org"
    _language: str = "english"

    def __init__(self, client: httpx.AsyncClient | None = None):
        super().__init__(client)

    def _get_url(self, word: str) -> str:
        return generate_link(self._base_url, f"/dictionary/{self._language}/{word}")

    def _get_media_url(self, route: str) -> str:
        return generate_link(self._base_url, route)

    async def _fetch_all_collocations_page(self, url: str) -> str:
        logger.debug("Fetching all collocations page: %s", url)
        try:
            res = await self._client.get(url)
        except httpx.RequestError as e:
            logger.error("Network error fetching collocations page %s: %s", url, e)
            raise CambridgeFetchException(str(e), url=url) from e
        if res.status_code == 404:
            raise CambridgeFetchException(
                "Collocations page not found", url=url, status_code=404
            )
        if res.status_code != 200:
            logger.warning(
                "Collocations page returned status %d for %s", res.status_code, url
            )
            raise CambridgeFetchException(url=url, status_code=res.status_code)
        if not res.text:
            logger.warning("Collocations page returned empty body for %s", url)
            raise CambridgeFetchException(
                "Empty response body", url=url, status_code=res.status_code
            )
        return res.text

    async def _fetch_dictionary_page(self, s: str) -> str:
        url = self._get_url(s)
        logger.debug("Fetching dictionary page for %r: %s", s, url)
        try:
            res = await self._client.get(url)
        except httpx.RequestError as e:
            logger.error("Network error fetching dictionary page for %r: %s", s, e)
            raise CambridgeFetchException(str(e), url=url) from e
        if res.status_code == 404:
            raise CambridgeWordNotFoundException(s)
        if res.status_code != 200:
            logger.warning(
                "Dictionary page returned status %d for %r", res.status_code, s
            )
            raise CambridgeFetchException(url=url, status_code=res.status_code)
        if not res.text:
            logger.warning("Dictionary page returned empty body for %r", s)
            raise CambridgeFetchException(
                "Empty response body", url=url, status_code=res.status_code
            )
        logger.debug("Fetched %d bytes for %r", len(res.text), s)
        return res.text

    def _get_source(self, tag: Tag) -> CambridgeSource | None:
        from_wrapper = tag.find(class_=["dsource"])
        if not from_wrapper:
            return None
        from_text = None
        from_link = None
        for a_link in from_wrapper.find_all(class_=["a", "dsource_e"]):
            from_link = a_link.get("href")
            from_text = a_link.text
            break
        if not from_text:
            return None
        return CambridgeSource(from_=from_text, link=from_link)

    def _get_page_sections(self, html: str) -> list[tuple[CambridgeSectionType, Tag]]:
        soup = BeautifulSoup(html, "html.parser")
        sections: list[tuple[CambridgeSectionType, Tag]] = []

        for section in soup.find_all(class_="pr di superentry"):
            # The headings are specified with c_hh, it's a yellow bacgrounded title-like text; in .superentry, it always appears at the top of the section.
            # The British doesn't have any headings(it's default), that's why if no section_heading is found, we consider it to be the British section.
            section_heading = section.find(class_="c_hh")
            section_type = CambridgeSectionType.British
            if section_heading:
                # Format: {search term} | Section Title (e.g. Business English)
                section_heading = section_heading.text.split("|")[-1]
                section_heading = section_heading.strip()
                section_type = CambridgeSectionType.from_cambridge_text(section_heading)

            sections.append((section_type, section))

        logger.debug("Found %d section(s): %s", len(sections), [s[0] for s in sections])
        return sections

    def _get_cefr_level(self, tag: Tag) -> CEFRLevel | None:
        # I have no idea what does .epp-xref.dxref stand for but it's always wrapping the CEFR level so who cares? (I do, the fuck?)
        cefr = tag.select(".epp-xref.dxref")
        if cefr:
            text = cefr[0].get_text().strip()
            try:
                return CEFRLevel(text)
            except ValueError:
                logger.debug("Unknown CEFR level: %r", text)
                return None
        return None

    def _crawl_definition_images(self, tag: Tag) -> list[str] | None:
        image_urls: list[str] = []
        # Cambridge uses AMP for definition images
        for image_elem in tag.find_all("amp-img", recursive=True):
            image_route = image_elem.get("src")
            if not image_route:
                continue
            image_url = self._get_media_url(image_route.split("?")[0])
            image_urls.append(image_url)
        return image_urls if image_urls else None

    def _crawl_definitions(self, tag: Tag) -> list[CambridgeDefinition]:
        definitions: list[CambridgeDefinition] = []
        for definition_block in tag.find_all(class_="def-block ddef_block"):
            definition_elem = definition_block.find(class_="def ddef_d db")
            if not definition_elem:
                logger.debug("Skipping definition block with no def element")
                continue
            examples: list[CambridgeDefinitionExample] = []
            for example_elem in definition_block.find_all(class_="examp dexamp"):
                example_phrase_elem = example_elem.find(class_="lu dlu")
                example_example_elem = example_elem.find(class_="eg deg")
                if not example_phrase_elem and not example_example_elem:
                    continue
                examples.append(
                    CambridgeDefinitionExample(
                        phrase=(
                            example_phrase_elem.get_text().strip()
                            if example_phrase_elem
                            else None
                        ),
                        example=(
                            example_example_elem.get_text().strip()
                            if example_example_elem
                            else None
                        ),
                    )
                )
            definition = definition_elem.text.strip(": ")
            definitions.append(
                CambridgeDefinition(
                    definition=definition,
                    examples=examples,
                    image_urls=self._crawl_definition_images(definition_block),
                )
            )
        return definitions

    def _crawl_section_senses(self, entry: Tag) -> list[CambridgeSense]:
        senses: list[CambridgeSense] = []
        for sense in entry.select(".pr.dsense"):
            cefr = self._get_cefr_level(sense)
            definition = self._crawl_definitions(sense)
            senses.append(
                CambridgeSense(
                    cefr=cefr,
                    definitions=definition,
                )
            )
        return senses

    def _crawl_pronunciations(self, entry: Tag) -> list[CambridgePronunciation] | None:
        pronunciations: list[CambridgePronunciation] = []
        for pron in entry.find_all(class_="dpron-i"):
            region_elem = pron.find(class_="region")
            pronunciation_elem = pron.find(class_="pron dpron")

            audio_urls: list[str] = []
            for audio_elem in pron.find_all("source"):
                audio_route = audio_elem.get("src")
                if not audio_route:
                    continue
                audio_url = self._get_media_url(audio_route)
                audio_urls.append(audio_url)

            pronunciations.append(
                CambridgePronunciation(
                    pronunciation=(
                        pronunciation_elem.get_text().strip()
                        if pronunciation_elem
                        else ""
                    ),
                    audio_urls=audio_urls,
                    region=region_elem.get_text().strip() if region_elem else "",
                )
            )
        return pronunciations if pronunciations else None

    def _crawl_verb_forms(self, entry: Tag) -> list[CambridgeVerbForm] | None:
        forms: list[CambridgeVerbForm] = []
        for form_group in entry.find_all(class_="inf-group dinfg"):
            name_elem = form_group.find(class_="lab dlab")
            form_elem = form_group.find(class_="inf dinf")
            if not form_elem:
                continue
            forms.append(
                CambridgeVerbForm(
                    form=form_elem.get_text().strip(),
                    name=name_elem.get_text().strip() if name_elem else None,
                )
            )
        return forms if forms else None

    def _crawl_section_phrases(self, entry: Tag) -> list[CambridgeSectionPhrase] | None:
        phrases: list[CambridgeSectionPhrase] = []
        for phrase in entry.find_all(class_=["phrase-block", "dphrase-block"]):
            headword = phrase.find(class_="phrase-title dphrase-title")
            definitions = self._crawl_definitions(phrase)
            phrases.append(
                CambridgeSectionPhrase(
                    headword=headword.get_text().strip() if headword else None,
                    definitions=definitions,
                )
            )
        return phrases if phrases else None

    def _crawl_section_idioms(self, entry: Tag) -> list[str] | None:
        idioms: list[str] = []
        for idioms_wrapper in entry.find_all(class_=["idioms"]):
            for idiom_elem in idioms_wrapper.find_all(class_=["item"]):
                idiom_text = idiom_elem.get_text().strip()
                if idiom_text:
                    idioms.append(idiom_text)
        return idioms if idioms else None

    def _crawl_section_phrasal_verbs(self, entry: Tag) -> list[str] | None:
        phrasal_verbs: list[str] = []
        for phrasal_verbs_wrapper in entry.find_all(class_=["phrasal_verbs"]):
            for phrasal_verb_elem in phrasal_verbs_wrapper.find_all(class_=["item"]):
                phrasal_verb_text = phrasal_verb_elem.get_text().strip()
                if phrasal_verb_text:
                    phrasal_verbs.append(phrasal_verb_text)
        return phrasal_verbs if phrasal_verbs else None

    def _crawl_section(
        self, section_type: CambridgeSectionType, section: Tag
    ) -> CambridgeSection:
        entries: list[CambridgeEntry] = []
        for entry in section.select(".entry-body__el, .di-body"):
            # for all the part of speeches, the whole body is going to be wrapped in .entry-body__el; but for idioms, it's wrapped in .di-body
            headword_elem = entry.find(class_="headword")
            pos_elem = entry.find(class_="pos dpos")
            if not headword_elem or not pos_elem:
                continue

            headword = headword_elem.get_text()
            part_of_speech = pos_elem.get_text()
            senses = self._crawl_section_senses(entry)
            pronunciations = self._crawl_pronunciations(entry)
            phrases = self._crawl_section_phrases(entry)
            verb_forms = self._crawl_verb_forms(entry)
            idioms = self._crawl_section_idioms(entry)
            phrasal_verbs = self._crawl_section_phrasal_verbs(entry)
            entries.append(
                CambridgeEntry(
                    headword=headword,
                    part_of_speech=part_of_speech,
                    senses=senses,
                    pronunciations=pronunciations,
                    verb_forms=verb_forms,
                    phrases=phrases,
                    idioms=idioms,
                    phrasal_verbs=phrasal_verbs,
                )
            )
        return CambridgeSection(
            type=section_type,
            entries=entries,
        )

    def _crawl_examples(self, html: str) -> list[CambridgeExample] | None:
        soup = BeautifulSoup(html, "html.parser")
        examples_wrapper = soup.find(id="dataset-example")
        if not examples_wrapper:
            return None

        examples: list[CambridgeExample] = []
        for example_wrapper in examples_wrapper.find_all(class_="lbb lb-cm lpt-10"):
            example_elem = example_wrapper.find(class_="deg")
            if not example_elem:
                continue

            examples.append(
                CambridgeExample(
                    example=example_elem.get_text().strip(),
                    source=self._get_source(example_wrapper),
                )
            )
        return examples if examples else None

    def _crawl_collocations(self, wrapper: Tag) -> list[CambridgeCollocation] | None:
        collocations: list[CambridgeCollocation] = []
        for collocation_wrapper in wrapper.select(".lbb.lb-cm.lpt-10"):
            collocation_elem = collocation_wrapper.find(class_="hdib tb lmb-10")
            example_elem = collocation_wrapper.find(class_="dexamp")

            if not collocation_elem or not example_elem:
                continue

            collocations.append(
                CambridgeCollocation(
                    collocation=collocation_elem.get_text().strip(),
                    example=example_elem.get_text().strip(),
                    source=self._get_source(collocation_wrapper),
                )
            )
        return collocations if collocations else None

    async def _get_collocations(self, html: str) -> list[CambridgeCollocation] | None:
        soup = BeautifulSoup(html, "html.parser")
        collocations_tag = soup.find(id="dataset_combinations")
        if not collocations_tag:
            logger.debug("No collocations dataset found")
            return None
        collocations_wrapper = collocations_tag.parent
        if not collocations_wrapper:
            logger.debug("No collocations wrapper found")
            return None

        # Cambridge includes a few of the collocations inline, then uses a button to redirect user to a page which contains all the collocations for the target search term.
        all_collocations_button = collocations_wrapper.find(
            class_="hao hbtn hbtn-tab bh tc-w tb lmt-5"
        )
        if all_collocations_button:
            all_collocations_link = all_collocations_button.get("href")
            if all_collocations_link:
                logger.debug(
                    "Fetching all collocations page: %s", all_collocations_link
                )
                try:
                    html = await self._fetch_all_collocations_page(
                        all_collocations_link
                    )
                except CambridgeFetchException:
                    logger.warning(
                        "Failed to fetch all collocations page, using inline data"
                    )
                else:
                    soup = BeautifulSoup(html, "html.parser")
                    page_content = soup.find(id="page-content")
                    if page_content:
                        collocations_wrapper = page_content

        collocations_body = collocations_wrapper.find(class_="cpexamps-body")
        if not collocations_body:
            logger.warning("No collocations body found")
            return None
        return self._crawl_collocations(collocations_body)

    async def crawl(self, word: str) -> CambridgePage:
        logger.info("Crawling %r", word)
        html = await self._fetch_dictionary_page(word)
        try:
            sections = self._get_page_sections(html)
        except Exception as e:
            raise CambridgeParseException(
                "Failed to parse page sections", word=word, detail=str(e)
            ) from e
        try:
            # TODO: Just like collocations, examples are also paginated, we should fetch all the pages and combine them into one list.
            examples = self._crawl_examples(html)
        except Exception as e:
            logger.warning("Failed to parse examples for %r: %s", word, e)
            examples = None
        try:
            collocations = await self._get_collocations(html)
        except CambridgeException:
            raise
        except Exception as e:
            logger.warning("Failed to parse collocations for %r: %s", word, e)
            collocations = None

        result = CambridgePage(
            search_term=word, sections=[], examples=examples, collocations=collocations
        )
        for section_type, section in sections:
            try:
                result.sections.append(self._crawl_section(section_type, section))
            except Exception as e:
                logger.warning(
                    "Failed to crawl section %s for %r: %s", section_type.value, word, e
                )

        logger.info(
            "Crawl complete for %r: %d section(s), %d example(s), %d collocation(s)",
            word,
            len(result.sections),
            len(result.examples) if result.examples else 0,
            len(result.collocations) if result.collocations else 0,
        )
        return result
