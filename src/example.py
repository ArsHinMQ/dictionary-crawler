import asyncio

from dictionary_crawler import CambridgeCrawler


async def main():
    async with CambridgeCrawler() as crawler:
        page = await crawler.crawl("run")

        print(f"Search term: {page.search_term}")
        print(f"Sections: {len(page.sections)}")

        for section in page.sections:
            print(f"\n--- {section.type.value} ---")
            for entry in section.entries:
                print(f"\n  {entry.headword} ({entry.part_of_speech})")

                if entry.pronunciations:
                    for p in entry.pronunciations:
                        print(f"    [{p.region}] {p.pronunciation}")
                        for url in p.audio_urls:
                            print(f"      audio: {url}")

                for sense in entry.senses:
                    level = sense.cefr.value if sense.cefr else "?"
                    print(f"    CEFR: {level}")
                    for defn in sense.definitions:
                        print(f"      - {defn.definition}")
                        if defn.examples:
                            for ex in defn.examples:
                                if ex.example:
                                    print(f"        e.g. {ex.example}")

                if entry.phrases:
                    print("    Phrases:")
                    for phrase in entry.phrases:
                        if phrase.headword:
                            print(f"      * {phrase.headword}")

                if entry.idioms:
                    print(f"    Idioms: {entry.idioms}")

                if entry.phrasal_verbs:
                    print(f"    Phrasal verbs: {entry.phrasal_verbs}")

        if page.examples:
            print("\n--- Examples ---")
            for ex in page.examples:
                print(f"  {ex.example}")
                if ex.source:
                    print(f"    from: {ex.source.from_} ({ex.source.link})")

        if page.collocations:
            print("\n--- Collocations ---")
            for col in page.collocations:
                print(f"  {col.collocation}")
                print(f"    e.g. {col.example}")

        print("\n--- JSON output ---")
        print(page.model_dump_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
