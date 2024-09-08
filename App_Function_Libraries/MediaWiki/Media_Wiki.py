# Media_Wiki.py
# Description: This file contains the functions to import MediaWiki dumps into the media_db and Chroma databases.
#
# Imports
#
#######################################################################################################################
import asyncio
import json
import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Iterator

import mwparserfromhell
import mwxml
import yaml
from tqdm import tqdm

# FIXME Add check_media_exists to DB_Manager.py
from App_Function_Libraries.DB.DB_Manager import add_media_with_keywords, check_media_exists
from App_Function_Libraries.RAG.ChromaDB_Library import process_and_store_content

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Load configuration
def load_mediawiki_import_config():
    with open('Config_Files\\mediawiki_import_config.yaml', 'r') as f:
        return yaml.safe_load(f)


config = load_mediawiki_import_config()


def parse_mediawiki_dump(file_path: str, namespaces: List[int] = None, skip_redirects: bool = False) -> Iterator[
    Dict[str, Any]]:
    dump = mwxml.Dump.from_file(open(file_path, encoding='utf-8'))
    total_pages = sum(1 for _ in dump.pages)  # Count total pages

    with tqdm(total=total_pages, desc="Parsing MediaWiki dump") as pbar:
        for page in dump.pages:
            if skip_redirects and page.redirect:
                continue
            if namespaces and page.namespace not in namespaces:
                continue

            for revision in page:
                code = mwparserfromhell.parse(revision.text)
                text = code.strip_code(normalize=True, collapse=True, keep_template_params=False)
                yield {
                    "title": page.title,
                    "content": text,
                    "namespace": page.namespace,
                    "page_id": page.id,
                    "revision_id": revision.id,
                    "timestamp": revision.timestamp
                }
            pbar.update(1)


def optimized_chunking(text: str, chunk_options: Dict[str, Any]) -> List[Dict[str, Any]]:
    sections = re.split(r'\n==\s*(.*?)\s*==\n', text)
    chunks = []
    current_chunk = ""
    current_size = 0

    for i in range(0, len(sections), 2):
        section_title = sections[i] if i > 0 else "Introduction"
        section_content = sections[i + 1] if i + 1 < len(sections) else ""

        if current_size + len(section_content) > chunk_options['max_size']:
            if current_chunk:
                chunks.append({"text": current_chunk, "metadata": {"section": section_title}})
            current_chunk = section_content
            current_size = len(section_content)
        else:
            current_chunk += f"\n== {section_title} ==\n" + section_content
            current_size += len(section_content)

    if current_chunk:
        chunks.append({"text": current_chunk, "metadata": {"section": "End"}})

    return chunks


async def process_mediawiki_content_async(content: List[Dict[str, Any]], wiki_name: str, chunk_options: Dict[str, Any],
                                          single_item: bool = False):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        if single_item:
            combined_content = "\n\n".join([f"# {item['title']}\n\n{item['content']}" for item in content])
            combined_title = f"MediaWiki Dump: {wiki_name}"
            await loop.run_in_executor(executor, process_single_item, combined_content, combined_title, wiki_name,
                                       chunk_options, True)
        else:
            tasks = [
                loop.run_in_executor(
                    executor,
                    process_single_item,
                    item['content'],
                    item['title'],
                    wiki_name,
                    chunk_options,
                    False,
                    item
                )
                for item in content
            ]
            await asyncio.gather(*tasks)


def process_single_item(content: str, title: str, wiki_name: str, chunk_options: Dict[str, Any],
                        is_combined: bool = False, item: Dict[str, Any] = None):
    url = f"mediawiki:{wiki_name}" if is_combined else f"mediawiki:{wiki_name}:{title}"

    if not check_media_exists(title, url):
        media_id = add_media_with_keywords(
            url=url,
            title=title,
            media_type="mediawiki_dump" if is_combined else "mediawiki_article",
            content=content,
            keywords=f"mediawiki,{wiki_name}" + (",full_dump" if is_combined else ",article"),
            prompt="",
            summary="",
            transcription_model="",
            author="MediaWiki",
            ingestion_date=item['timestamp'].strftime('%Y-%m-%d') if item else None
        )

        chunks = optimized_chunking(content, chunk_options)
        for chunk in chunks:
            process_and_store_content(chunk['text'], f"mediawiki_{wiki_name}", media_id)
    else:
        logging.info(f"Skipping existing article: {title}")


def load_checkpoint(file_path: str) -> int:
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)['last_processed_id']
    return 0


def save_checkpoint(file_path: str, last_processed_id: int):
    with open(file_path, 'w') as f:
        json.dump({'last_processed_id': last_processed_id}, f)


async def import_mediawiki_dump(
        file_path: str,
        wiki_name: str,
        namespaces: List[int] = None,
        skip_redirects: bool = False,
        chunk_options: Dict[str, Any] = None,
        single_item: bool = False
) -> str:
    try:
        if chunk_options is None:
            chunk_options = config['chunking']

        checkpoint_file = f"{wiki_name}_import_checkpoint.json"
        last_processed_id = load_checkpoint(checkpoint_file)

        content = []
        for item in parse_mediawiki_dump(file_path, namespaces, skip_redirects):
            if item['page_id'] <= last_processed_id:
                continue
            content.append(item)
            if len(content) >= 1000:  # Process in batches of 1000
                await process_mediawiki_content_async(content, wiki_name, chunk_options, single_item)
                save_checkpoint(checkpoint_file, content[-1]['page_id'])
                content.clear()

        if content:  # Process any remaining items
            await process_mediawiki_content_async(content, wiki_name, chunk_options, single_item)
            save_checkpoint(checkpoint_file, content[-1]['page_id'])

        os.remove(checkpoint_file)  # Remove checkpoint file after successful import
        return f"Successfully imported and indexed MediaWiki dump: {wiki_name}"
    except FileNotFoundError:
        logging.error(f"MediaWiki dump file not found: {file_path}")
        return f"Error: File not found - {file_path}"
    except PermissionError:
        logging.error(f"Permission denied when trying to read: {file_path}")
        return f"Error: Permission denied - {file_path}"
    except Exception as e:
        logging.exception(f"Unexpected error during MediaWiki import: {str(e)}")
        return f"Unexpected error: {str(e)}"

#
# End of Media_Wiki.py
#######################################################################################################################