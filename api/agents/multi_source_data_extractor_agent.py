import asyncio
import os
import sys
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

import aiohttp

# Ensure local imports resolve when deployed serverlessly
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Robust import to work in both direct and package contexts
try:
    from utils.vector_store_manager import VectorStoreManager  # noqa: E402
except ImportError:  # pragma: no cover - fallback for pytest/package
    from api.utils.vector_store_manager import VectorStoreManager  # type: ignore

from .data_extractor_agent import DataExtractorAgent  # reuse CORE logic without modifying it


@dataclass
class MultiSourceExtractorConfig:
    max_results: int = 30
    per_source_limit: int = 20
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    language: Optional[str] = None
    research_domain: str = "General"
    sources: Optional[List[str]] = None  # ["core", "openalex", "europe_pmc", "arxiv"]
    enrich_with: Optional[List[str]] = None  # ["crossref", "unpaywall", "sem_scholar"]
    oa_only: bool = True
    auto_fallback: bool = True
    collection_name: str = "ResearchPaper"


@dataclass
class SourceStats:
    name: str
    fetched: int = 0
    errors: int = 0
    details: List[str] = field(default_factory=list)
    results: List[Dict[str, Any]] = field(default_factory=list)


class MultiSourceDataExtractorAgent:
    """
    Multi-source academic data extractor.

    - Discovery providers (free): CORE (existing), OpenAlex, Europe PMC, arXiv
    - Enrichment providers (free): Crossref, Unpaywall, Semantic Scholar

    This class is self-contained and does NOT modify existing agents.
    """

    def __init__(self, collection_name: str = "ResearchPaper", research_domain: str = "General") -> None:
        self.collection_name = collection_name
        self.research_domain = research_domain
        # Lazy-init vector store to avoid noisy logs if store=False
        self.vector_store_manager: Optional[VectorStoreManager] = None
        self._concurrency_limit = int(os.getenv("EXTRACTOR_CONCURRENCY", "8"))
        self._sem = asyncio.Semaphore(self._concurrency_limit)

    # Helper to reconstruct OpenAlex abstract text from inverted index
    @staticmethod
    def _reconstruct_openalex_abstract(abstract_field: Any) -> Optional[str]:
        if isinstance(abstract_field, str):
            return abstract_field
        inv = abstract_field
        if not isinstance(inv, dict) or not inv:
            return None
        try:
            max_pos = -1
            for _, positions in inv.items():
                for pos in positions:
                    if isinstance(pos, int) and pos > max_pos:
                        max_pos = pos
            if max_pos < 0:
                return None
            tokens: List[str] = [""] * (max_pos + 1)
            for word, positions in inv.items():
                for pos in positions:
                    if isinstance(pos, int) and 0 <= pos <= max_pos:
                        tokens[pos] = word
            text = " ".join(t for t in tokens if isinstance(t, str))
            return text.strip() or None
        except Exception:
            return None

    async def run(
        self,
        query: str,
        research_domain: str = "General",
        max_results: int = 30,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        language: Optional[str] = None,
        sources: Optional[List[str]] = None,
        enrich_with: Optional[List[str]] = None,
        per_source_limit: int = 20,
        oa_only: bool = True,
        auto_fallback: bool = True,
        store: bool = True,
        full_text: Optional[bool] = None,
        use_playwright_fallback: bool = False,
    ) -> Dict[str, Any]:
        started_at = datetime.now(timezone.utc).isoformat()

        config = MultiSourceExtractorConfig(
            max_results=max_results,
            per_source_limit=per_source_limit,
            year_from=year_from,
            year_to=year_to,
            language=language,
            research_domain=research_domain,
            sources=sources,
            enrich_with=enrich_with,
            oa_only=oa_only,
            auto_fallback=auto_fallback,
            collection_name=self.collection_name,
        )

        # Defaults: AUTO mode if not specified -> openalex + europe_pmc + arxiv + core
        selected_sources = set((sources or ["openalex", "europe_pmc", "arxiv", "core"]))
        selected_enrichers = set((enrich_with or ["crossref", "unpaywall", "sem_scholar"]))
        print(f"[MULTI] Selected sources: {sorted(selected_sources)}")
        print(f"[MULTI] Selected enrichers: {sorted(selected_enrichers)}")
        print(f"[MULTI] Playwright fallback enabled: {use_playwright_fallback}")

        discovery_stats: List[SourceStats] = []
        enrichment_stats: List[SourceStats] = []

        # Run discovery
        items: List[Dict[str, Any]] = []
        seen_dois: Set[str] = set()
        seen_hashes: Set[str] = set()

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
            discovery_tasks: List[asyncio.Task] = []

            if "core" in selected_sources:
                print("[DISCOVERY] Starting CORE...")
                print(f"[DISCOVERY] CORE params: query='{query}', max_results={config.per_source_limit}, year_from={config.year_from}, year_to={config.year_to}")
                discovery_tasks.append(asyncio.create_task(
                    self._discover_core(query, config)
                ))

            if "openalex" in selected_sources:
                print("[DISCOVERY] Starting OpenAlex...")
                discovery_tasks.append(asyncio.create_task(
                    self._discover_openalex(session, query, config)
                ))

            if "europe_pmc" in selected_sources:
                print("[DISCOVERY] Starting Europe PMC...")
                discovery_tasks.append(asyncio.create_task(
                    self._discover_europe_pmc(session, query, config)
                ))

            if "arxiv" in selected_sources:
                print("[DISCOVERY] Starting arXiv...")
                discovery_tasks.append(asyncio.create_task(
                    self._discover_arxiv(session, query, config)
                ))

            # Collect discovery
            discovery_results = await asyncio.gather(*discovery_tasks, return_exceptions=True)
            for result in discovery_results:
                if isinstance(result, tuple):
                    src_name, docs, stats = result
                    print(f"[DISCOVERY] Completed {src_name}: fetched={len(docs)} errors={stats.errors}")
                    # Print actual returned data (first two docs key fields)
                    for i, d in enumerate(docs[:2], 1):
                        preview = {
                            "title": (d.get("title") or "")[:120],
                            "doi": d.get("doi"),
                            "year": d.get("year"),
                            "url": d.get("url"),
                            "source": d.get("source"),
                        }
                        print(f"[DISCOVERY][{src_name}] doc{i}: {json.dumps(preview, ensure_ascii=False)}")
                    discovery_stats.append(stats)
                    for d in docs:
                        doi = (d.get("doi") or "").lower().strip()
                        if doi and doi in seen_dois:
                            continue
                        if doi:
                            seen_dois.add(doi)
                        else:
                            # Basic hash from title+year
                            h = f"{(d.get('title') or '').strip().lower()}::{d.get('year') or ''}"
                            if h in seen_hashes:
                                continue
                            seen_hashes.add(h)
                        items.append(d)
                        if len(items) >= config.max_results:
                            break
                elif isinstance(result, Exception):
                    # In case of provider-level failure
                    print(f"[DISCOVERY] Provider error: {result}")
                    discovery_stats.append(SourceStats(name="unknown", fetched=0, errors=1, details=[str(result)]))

        # Early exit if nothing found and fallback is enabled: widen years once
        if not items and config.auto_fallback:
            print("[DISCOVERY] No items found. Retrying with relaxed filters (no year, OA off)...")
            retry_cfg = MultiSourceExtractorConfig(**{**config.__dict__, "year_from": None, "year_to": None, "oa_only": False})
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
                discovery_tasks_2: List[asyncio.Task] = []
                if "openalex" in selected_sources:
                    discovery_tasks_2.append(asyncio.create_task(self._discover_openalex(session, query, retry_cfg)))
                if "europe_pmc" in selected_sources:
                    discovery_tasks_2.append(asyncio.create_task(self._discover_europe_pmc(session, query, retry_cfg)))
                if "arxiv" in selected_sources:
                    discovery_tasks_2.append(asyncio.create_task(self._discover_arxiv(session, query, retry_cfg)))
                if "core" in selected_sources:
                    discovery_tasks_2.append(asyncio.create_task(self._discover_core(query, retry_cfg)))
                discovery_results_2 = await asyncio.gather(*discovery_tasks_2, return_exceptions=True)
                for result in discovery_results_2:
                    if isinstance(result, tuple):
                        src_name, docs, stats = result
                        print(f"[DISCOVERY][RETRY] Completed {src_name}: fetched={len(docs)} errors={stats.errors}")
                        discovery_stats.append(stats)
                        for d in docs:
                            doi = (d.get("doi") or "").lower().strip()
                            if doi and doi in seen_dois:
                                continue
                            if doi:
                                seen_dois.add(doi)
                            else:
                                h = f"{(d.get('title') or '').strip().lower()}::{d.get('year') or ''}"
                                if h in seen_hashes:
                                    continue
                                seen_hashes.add(h)
                            items.append(d)
                            if len(items) >= config.max_results:
                                break
                    elif isinstance(result, Exception):
                        print(f"[DISCOVERY][RETRY] Provider error: {result}")
                        discovery_stats.append(SourceStats(name="unknown", fetched=0, errors=1, details=[str(result)]))

        # Enrichment
        if items and selected_enrichers:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
                # Crossref first (normalize)
                if "crossref" in selected_enrichers:
                    print("[ENRICH] Starting Crossref...")
                    stats = await self._enrich_crossref(session, items)
                    print(f"[ENRICH] Completed Crossref: fetched={stats.fetched} errors={stats.errors}")
                    # Print first two enriched docs with metadata
                    count = 0
                    for d in items:
                        if d.get("metadata"):
                            print(f"[ENRICH][Crossref] doc: {json.dumps({'doi': d.get('doi'), 'journal': d['metadata'].get('journal'), 'publisher': d['metadata'].get('publisher')}, ensure_ascii=False)}")
                            count += 1
                            if count >= 2:
                                break
                    enrichment_stats.append(stats)
                # Unpaywall (oa link)
                if "unpaywall" in selected_enrichers:
                    print("[ENRICH] Starting Unpaywall...")
                    stats = await self._enrich_unpaywall(session, items)
                    print(f"[ENRICH] Completed Unpaywall: fetched={stats.fetched} errors={stats.errors}")
                    # Print first two OA links
                    count = 0
                    for d in items:
                        oa = (d.get("links") or {}).get("oa_pdf")
                        if oa:
                            print(f"[ENRICH][Unpaywall] doc: {json.dumps({'doi': d.get('doi'), 'oa_pdf': oa}, ensure_ascii=False)}")
                            count += 1
                            if count >= 2:
                                break
                    enrichment_stats.append(stats)
                # Semantic Scholar (signals)
                if "sem_scholar" in selected_enrichers:
                    print("[ENRICH] Starting Semantic Scholar...")
                    stats = await self._enrich_semantic_scholar(session, items)
                    print(f"[ENRICH] Completed Semantic Scholar: fetched={stats.fetched} errors={stats.errors}")
                    # Print first two signals
                    count = 0
                    for d in items:
                        if d.get("signals"):
                            print(f"[ENRICH][SemScholar] doc: {json.dumps({'doi': d.get('doi'), **d['signals']}, ensure_ascii=False)}")
                            count += 1
                            if count >= 2:
                                break
                    enrichment_stats.append(stats)

        # Store to vector store if requested
        stored = 0
        if items and store:
            try:
                if self.vector_store_manager is None:
                    self.vector_store_manager = VectorStoreManager(collection_name=self.collection_name,
                                                                     research_domain=self.research_domain)
                # Normalize research_domain
                for doc in items:
                    doc.setdefault("research_domain", research_domain)

                # Auto behavior: if full_text is None, attempt full-text for docs with a PDF, then store abstracts for the rest
                if full_text is None:
                    # Try full-text first where possible
                    stored_full = await self._extract_and_store_full_text(items, research_domain, use_playwright_fallback)
                    # Then store abstracts only for items without an available PDF link
                    chunks: List[str] = []
                    meta_list: List[Dict[str, Any]] = []
                    for d in items:
                        if self._select_pdf_url(d):
                            continue
                        # Attempt to resolve abstract via Playwright if missing
                        content = d.get("abstract") or ""
                        if not content and use_playwright_fallback:
                            resolved = await self._extract_abstract_with_playwright(d.get("url") or "")
                            print(f"[DEBUG] Resolved playwright abstract: {resolved}")
                            if resolved:
                                content = resolved
                        if not content:
                            continue
                        chunks.append(content)
                        meta_list.append({
                            "title": d.get("title", ""),
                            "authors": d.get("authors", ""),
                            "year": d.get("year") or 0,
                            "doi": d.get("doi", ""),
                            "source": d.get("source", ""),
                            "paper_id": d.get("paper_id", ""),
                            "chunk_index": 0,
                        })
                    if chunks:
                        self.vector_store_manager.add_chunks(chunks, meta_list)
                        stored = stored_full + len(chunks)
                elif full_text:
                    # Attempt to download OA PDFs and store extracted chunks
                    stored = await self._extract_and_store_full_text(items, research_domain, use_playwright_fallback)
                else:
                    # Store minimal abstracts as small chunks (metadata-first)
                    chunks: List[str] = []
                    meta_list: List[Dict[str, Any]] = []
                    for d in items:
                        content = d.get("abstract") or ""
                        if not content and use_playwright_fallback:
                            resolved = await self._extract_abstract_with_playwright(d.get("url") or "")
                            if resolved:
                                content = resolved
                        if not content:
                            continue
                        chunks.append(content)
                        meta_list.append({
                            "title": d.get("title", ""),
                            "authors": d.get("authors", ""),
                            "year": d.get("year") or 0,
                            "doi": d.get("doi", ""),
                            "source": d.get("source", ""),
                            "paper_id": d.get("paper_id", ""),
                            "chunk_index": 0,
                        })
                    if chunks:
                        self.vector_store_manager.add_chunks(chunks, meta_list)
                        stored = len(chunks)
            except Exception as e:
                print(f"[STORE] Error storing documents: {e}")
                enrichment_stats.append(SourceStats(name="storage", fetched=0, errors=1, details=[str(e)]))

        print(f"[MULTI] Completed. total_items={len(items)} stored={stored}")
        return {
            "success": True,
            "data": {
                "query": query,
                "research_domain": research_domain,
                "documents": items[: config.max_results],
                "total_found": len(items),
                "stored": stored,
                "source_stats": [s.__dict__ for s in discovery_stats],
                "enrichment_stats": [s.__dict__ for s in enrichment_stats],
                "started_at": started_at,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ----------------------------- Discovery providers -----------------------------

    async def _discover_core(self, query: str, cfg: MultiSourceExtractorConfig):
        name = "core"
        stats = SourceStats(name=name)
        try:
            agent = DataExtractorAgent()
            # Respect per_source_limit to avoid long scrolls
            max_results = min(cfg.per_source_limit, cfg.max_results)
            papers = await agent.fetch_papers(query, max_results=max_results, year_from=cfg.year_from, year_to=cfg.year_to)
            results: List[Dict[str, Any]] = []
            for p in papers or []:
                # Robustly build authors string (handle list of dicts or strings)
                raw_authors = p.get("authors")
                authors_str = ""
                if isinstance(raw_authors, str):
                    authors_str = raw_authors
                elif isinstance(raw_authors, list):
                    names: List[str] = []
                    for a in raw_authors:
                        if isinstance(a, dict):
                            n = a.get("name") or a.get("fullName") or a.get("full_name") or a.get("display_name") or ""
                            if n:
                                names.append(str(n))
                        else:
                            names.append(str(a))
                    authors_str = ", ".join([n for n in names if n])

                results.append({
                    "title": p.get("title", "Unknown Title"),
                    "authors": authors_str,
                    "year": p.get("year"),
                    "abstract": p.get("abstract", ""),
                    "doi": (p.get("doi") or "").lower().strip(),
                    "source": name,
                    "url": p.get("downloadUrl") or p.get("pdfUrl") or p.get("url") or None,
                })
            stats.fetched = len(results)
            return name, results, stats
        except Exception as e:
            stats.errors += 1
            stats.details.append(str(e))
            return name, [], stats

    async def _discover_openalex(self, session: aiohttp.ClientSession, query: str, cfg: MultiSourceExtractorConfig):
        name = "openalex"
        stats = SourceStats(name=name)
        try:
            params = {
                "search": query,
                "per_page": min(cfg.per_source_limit, cfg.max_results),
            }
            if cfg.year_from or cfg.year_to:
                yfrom = cfg.year_from or 1900
                yto = cfg.year_to or datetime.now().year
                params["from_publication_date"] = f"{yfrom}-01-01"
                params["to_publication_date"] = f"{yto}-12-31"
            if cfg.language:
                params["language"] = cfg.language

            # OpenAlex prefers a contact email via mailto parameter and UA
            mailto = os.getenv("OPENALEX_MAILTO") or os.getenv("UNPAYWALL_EMAIL") or ""
            if mailto:
                params["mailto"] = mailto

            url = "https://api.openalex.org/works"
            print(f"[DISCOVERY][OpenAlex] GET {url} params={params}")
            async with self._sem:
                ua = f"Waga-Academy-Extractor/1.0 ({mailto})" if mailto else "Waga-Academy-Extractor/1.0"
                async with session.get(url, params=params, headers={"User-Agent": ua, "Accept": "application/json"}) as resp:
                    if resp.status != 200:
                        stats.errors += 1
                        reason = f"HTTP {resp.status}"
                        if resp.status == 403 and not mailto:
                            reason += " (tip: set OPENALEX_MAILTO env to reduce blocks)"
                        stats.details.append(reason)
                        return name, [], stats
                    data = await resp.json()

            results = []
            for w in data.get("results", []) or []:
                doi = (w.get("doi") or "").replace("https://doi.org/", "").lower().strip()
                title = (w.get("display_name") or "").strip()
                year = None
                try:
                    if w.get("publication_year"):
                        year = int(w.get("publication_year"))
                except Exception:
                    year = None
                authors = ", ".join([a.get("author", {}).get("display_name", "") for a in (w.get("authorships") or [])])
                abstract_text = self._reconstruct_openalex_abstract(
                    w.get("abstract") or w.get("abstract_inverted_index")
                )
                results.append({
                    "title": title,
                    "authors": authors,
                    "year": year,
                    "abstract": abstract_text,
                    "doi": doi,
                    "source": name,
                    "url": w.get("primary_location", {}).get("landing_page_url") or w.get("id"),
                })
            stats.fetched = len(results)
            if results:
                samples = ", ".join([r.get("title","")[:100] for r in results[:2]])
                print(f"[DISCOVERY][OpenAlex] sample titles: {samples}")
            return name, results, stats
        except Exception as e:
            stats.errors += 1
            stats.details.append(str(e))
            return name, [], stats

    async def _discover_europe_pmc(self, session: aiohttp.ClientSession, query: str, cfg: MultiSourceExtractorConfig):
        name = "europe_pmc"
        stats = SourceStats(name=name)
        try:
            # Europe PMC REST
            params = {
                "query": query,
                "pageSize": str(min(cfg.per_source_limit, cfg.max_results)),
                "format": "json",
            }
            if cfg.year_from or cfg.year_to:
                yfrom = cfg.year_from or 1900
                yto = cfg.year_to or datetime.now().year
                params["query"] += f" PUB_YEAR:[{yfrom} TO {yto}]"
            if cfg.oa_only:
                params["query"] += " OPEN_ACCESS:y"

            url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
            print(f"[DISCOVERY][EuropePMC] GET {url} params={{'query': params['query'], 'pageSize': params['pageSize']}}")
            async with self._sem:
                async with session.get(url, params=params, headers={"User-Agent": "Waga-Academy-Extractor/1.0"}) as resp:
                    if resp.status != 200:
                        stats.errors += 1
                        stats.details.append(f"HTTP {resp.status}")
                        return name, [], stats
                    data = await resp.json()

            results = []
            for r in (data.get("resultList", {}) or {}).get("result", []) or []:
                doi = (r.get("doi") or "").lower().strip()
                title = (r.get("title") or "").strip()
                authors = r.get("authorString") or ""
                year = None
                try:
                    if r.get("pubYear"):
                        year = int(r.get("pubYear"))
                except Exception:
                    year = None
                results.append({
                    "title": title,
                    "authors": authors,
                    "year": year,
                    "abstract": r.get("abstractText"),
                    "doi": doi,
                    "source": name,
                    "url": r.get("fullTextUrlList", {}).get("fullTextUrl", [{}])[0].get("url") if r.get("fullTextUrlList") else r.get("pmcid") or r.get("id"),
                })
            stats.fetched = len(results)
            if results:
                samples = ", ".join([r.get("title","")[:100] for r in results[:2]])
                print(f"[DISCOVERY][EuropePMC] sample titles: {samples}")
            return name, results, stats
        except Exception as e:
            stats.errors += 1
            stats.details.append(str(e))
            return name, [], stats

    async def _discover_arxiv(self, session: aiohttp.ClientSession, query: str, cfg: MultiSourceExtractorConfig):
        name = "arxiv"
        stats = SourceStats(name=name)
        try:
            # arXiv API (Atom); use export.arxiv.org
            max_results = min(cfg.per_source_limit, cfg.max_results)
            url = "https://export.arxiv.org/api/query"
            params = {"search_query": f"all:{query}", "start": 0, "max_results": max_results}
            print(f"[DISCOVERY][arXiv] GET {url} params={params}")
            async with self._sem:
                async with session.get(url, params=params, headers={"User-Agent": "Waga-Academy-Extractor/1.0"}) as resp:
                    if resp.status != 200:
                        stats.errors += 1
                        stats.details.append(f"HTTP {resp.status}")
                        return name, [], stats
                    text = await resp.text()

            # Minimal parsing without extra deps
            # Extract entries by simple splits; robust enough for key fields
            results: List[Dict[str, Any]] = []
            for chunk in text.split("<entry>")[1:]:
                title = self._extract_between(chunk, "<title>", "</title>") or ""
                summary = self._extract_between(chunk, "<summary>", "</summary>") or ""
                doi = (self._extract_between(chunk, "<arxiv:doi>", "</arxiv:doi>") or "").lower().strip()
                year = None
                published = self._extract_between(chunk, "<published>", "</published>")
                if published:
                    try:
                        year = int(published[:4])
                    except Exception:
                        year = None
                pdf_url = None
                for line in chunk.splitlines():
                    if 'type="application/pdf"' in line and 'href=' in line:
                        pdf_url = self._extract_attr(line, 'href')
                        break
                results.append({
                    "title": title.strip(),
                    "authors": "",  # authors parsing omitted for brevity
                    "year": year,
                    "abstract": summary.strip(),
                    "doi": doi,
                    "source": name,
                    "url": pdf_url,
                })
            stats.fetched = len(results)
            if results:
                samples = ", ".join([r.get("title","")[:100] for r in results[:2]])
                print(f"[DISCOVERY][arXiv] sample titles: {samples}")
            return name, results, stats
        except Exception as e:
            stats.errors += 1
            stats.details.append(str(e))
            return name, [], stats

    # ----------------------------- Enrichment providers -----------------------------

    async def _enrich_crossref(self, session: aiohttp.ClientSession, items: List[Dict[str, Any]]) -> SourceStats:
        stats = SourceStats(name="crossref")
        base = "https://api.crossref.org/works/"
        tasks = []
        doi_list = []
        for doc in items:
            doi = (doc.get("doi") or "").strip()
            if not doi:
                continue
            doi_list.append(doi)
            tasks.append(self._throttled_get(session, f"{base}{doi}", headers={"User-Agent": "Waga-Academy-Extractor/1.0"}))
        if doi_list:
            print(f"[ENRICH][Crossref] DOIs: {doi_list}")

        responses = await asyncio.gather(*tasks, return_exceptions=True) if tasks else []
        for resp in responses:
            if isinstance(resp, dict) and resp.get("status") == 200 and resp.get("json"):
                try:
                    message = (resp["json"] or {}).get("message", {})
                    doi = (message.get("DOI") or "").lower().strip()
                    # Find doc by DOI
                    for d in items:
                        if (d.get("doi") or "").lower().strip() == doi:
                            d.setdefault("metadata", {})
                            d["metadata"].update({
                                "publisher": message.get("publisher"),
                                "journal": (message.get("container-title") or [None])[0],
                                "issn": (message.get("ISSN") or [None])[0] if message.get("ISSN") else None,
                            })
                            break
                    stats.fetched += 1
                    # Add compact result record
                    stats.results.append({
                        "doi": doi,
                        "publisher": message.get("publisher"),
                        "journal": (message.get("container-title") or [None])[0],
                        "issn": (message.get("ISSN") or [None])[0] if message.get("ISSN") else None,
                    })
                except Exception as e:
                    stats.errors += 1
                    stats.details.append(str(e))
            elif isinstance(resp, dict) and resp.get("status") is not None:
                stats.errors += 1
                stats.details.append(f"HTTP {resp.get('status')}")
            else:
                stats.errors += 1
        return stats

    async def _enrich_unpaywall(self, session: aiohttp.ClientSession, items: List[Dict[str, Any]]) -> SourceStats:
        stats = SourceStats(name="unpaywall")
        email = os.getenv("UNPAYWALL_EMAIL", "opensource@waga.local")
        tasks = []
        doi_list = []
        for doc in items:
            doi = (doc.get("doi") or "").strip()
            if not doi:
                continue
            doi_list.append(doi)
            url = f"https://api.unpaywall.org/v2/{doi}?email={email}"
            tasks.append(self._throttled_get(session, url, headers={"User-Agent": "Waga-Academy-Extractor/1.0"}))
        if doi_list:
            print(f"[ENRICH][Unpaywall] DOIs: {doi_list}")

        responses = await asyncio.gather(*tasks, return_exceptions=True) if tasks else []
        for resp in responses:
            if isinstance(resp, dict) and resp.get("status") == 200 and resp.get("json"):
                try:
                    data = resp["json"]
                    doi = (data.get("doi") or "").lower().strip()
                    best = data.get("best_oa_location") or {}
                    pdf_url = best.get("url_for_pdf") or best.get("url")
                    for d in items:
                        if (d.get("doi") or "").lower().strip() == doi:
                            if pdf_url:
                                d.setdefault("links", {})
                                d["links"]["oa_pdf"] = pdf_url
                            d.setdefault("metadata", {})
                            d["metadata"]["oa_status"] = data.get("oa_status")
                            break
                    stats.fetched += 1
                    stats.results.append({
                        "doi": doi,
                        "oa_pdf": pdf_url,
                        "oa_status": data.get("oa_status"),
                    })
                except Exception as e:
                    stats.errors += 1
                    stats.details.append(str(e))
            elif isinstance(resp, dict) and resp.get("status") is not None:
                stats.errors += 1
                stats.details.append(f"HTTP {resp.get('status')}")
            else:
                stats.errors += 1
        return stats

    async def _enrich_semantic_scholar(self, session: aiohttp.ClientSession, items: List[Dict[str, Any]]) -> SourceStats:
        stats = SourceStats(name="sem_scholar")
        api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
        headers = {"User-Agent": "Waga-Academy-Extractor/1.0"}
        if api_key:
            headers["x-api-key"] = api_key
        base = "https://api.semanticscholar.org/graph/v1/paper/"
        fields = "citationCount,influentialCitationCount,fieldsOfStudy"

        tasks = []
        doi_list = []
        for doc in items:
            doi = (doc.get("doi") or "").strip()
            if not doi:
                continue
            doi_list.append(doi)
            url = f"{base}DOI:{doi}?fields={fields}"
            tasks.append(self._throttled_get(session, url, headers=headers))
        if doi_list:
            print(f"[ENRICH][SemanticScholar] DOIs: {doi_list}")

        responses = await asyncio.gather(*tasks, return_exceptions=True) if tasks else []
        for resp in responses:
            if isinstance(resp, dict) and resp.get("status") == 200 and resp.get("json"):
                try:
                    data = resp["json"]
                    # Semantic Scholar returns canonical DOI in externalIds sometimes; we match by request DOI instead
                    doi = (data.get("externalIds", {}).get("DOI") or "").lower().strip()
                    for d in items:
                        if doi and (d.get("doi") or "").lower().strip() == doi:
                            d.setdefault("signals", {})
                            d["signals"].update({
                                "citationCount": data.get("citationCount"),
                                "influentialCitationCount": data.get("influentialCitationCount"),
                                "fieldsOfStudy": data.get("fieldsOfStudy"),
                            })
                            break
                    stats.fetched += 1
                    stats.results.append({
                        "doi": doi,
                        "citationCount": data.get("citationCount"),
                        "influentialCitationCount": data.get("influentialCitationCount"),
                        "fieldsOfStudy": data.get("fieldsOfStudy"),
                    })
                except Exception as e:
                    stats.errors += 1
                    stats.details.append(str(e))
            elif isinstance(resp, dict) and resp.get("status") is not None:
                stats.errors += 1
                stats.details.append(f"HTTP {resp.get('status')}")
            else:
                stats.errors += 1
        return stats

    # ----------------------------- Helpers -----------------------------

    async def _throttled_get(self, session: aiohttp.ClientSession, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """GET with concurrency control and simple retry/backoff."""
        max_attempts = 3
        backoff = 0.8
        for attempt in range(max_attempts):
            try:
                async with self._sem:
                    async with session.get(url, headers=headers) as resp:
                        status = resp.status
                        if status == 200:
                            try:
                                return {"status": status, "json": await resp.json()}
                            except Exception:
                                return {"status": status, "text": await resp.text()}
                        if status in (429, 500, 502, 503, 504):
                            await asyncio.sleep((backoff ** attempt) + 0.2 * attempt)
                            continue
                        return {"status": status}
            except asyncio.TimeoutError:
                await asyncio.sleep((backoff ** attempt) + 0.2 * attempt)
            except Exception as _:
                await asyncio.sleep((backoff ** attempt) + 0.2 * attempt)
        return {"status": 599}

    @staticmethod
    def _extract_between(text: str, start_tag: str, end_tag: str) -> Optional[str]:
        try:
            i = text.index(start_tag) + len(start_tag)
            j = text.index(end_tag, i)
            return text[i:j]
        except Exception:
            return None

    @staticmethod
    def _extract_attr(tag_line: str, attr: str) -> Optional[str]:
        try:
            # naive parse href="..."
            key = f"{attr}="
            if key not in tag_line:
                return None
            part = tag_line.split(key, 1)[1]
            quote = '"' if '"' in part else "'"
            start = part.index(quote) + 1
            end = part.index(quote, start)
            return part[start:end]
        except Exception:
            return None

    # ---------------- Full‑text extraction helpers ----------------
    async def _extract_and_store_full_text(self, items: List[Dict[str, Any]], research_domain: str, use_playwright_fallback: bool = False) -> int:
        import PyPDF2  # local import to avoid import cost if not used
        stored_chunks = 0
        timeout = aiohttp.ClientTimeout(total=25)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for doc in items:
                pdf_url = self._select_pdf_url(doc)
                # Try to resolve via Playwright when no direct PDF
                if not pdf_url and use_playwright_fallback:
                    landing = doc.get("url") or ""
                    if landing:
                        resolved = await self._resolve_pdf_with_playwright(landing)
                        if resolved and ".pdf" in resolved.lower():
                            pdf_url = resolved
                            # remember for later
                            doc.setdefault("links", {})
                            doc["links"]["oa_pdf"] = pdf_url
                if not pdf_url:
                    continue
                text = await self._download_and_extract_pdf_text(session, pdf_url)
                if not text:
                    continue
                # Chunk
                chunks = self._simple_chunk(text, chunk_size=2000, overlap=200)
                metadata_list: List[Dict[str, Any]] = []
                for i, _ in enumerate(chunks):
                    metadata_list.append({
                        "title": doc.get("title", ""),
                        "authors": doc.get("authors", ""),
                        "year": doc.get("year") or 0,
                        "doi": doc.get("doi", ""),
                        "source": doc.get("source", ""),
                        "paper_id": doc.get("paper_id", ""),
                        "chunk_index": i,
                    })
                try:
                    if chunks:
                        self.vector_store_manager.add_chunks(chunks, metadata_list)
                        stored_chunks += len(chunks)
                except Exception as e:
                    print(f"[STORE] Failed to store chunks for {pdf_url}: {e}")
        return stored_chunks

    async def _resolve_pdf_with_playwright(self, url: str) -> Optional[str]:
        if not url:
            return None
        try:
            from playwright.async_api import async_playwright  # type: ignore
        except Exception:
            print("[PLAYWRIGHT] Not installed or unavailable; skipping browser fallback")
            return None
        try:
            async with self._sem:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    context = await browser.new_context()
                    page = await context.new_page()
                    await page.goto(url, wait_until="networkidle", timeout=30000)
                    # Try meta tag first
                    meta = page.locator('meta[name="citation_pdf_url"]')
                    if await meta.count():
                        href = await meta.first.get_attribute("content")
                        if href and href.lower().endswith(".pdf"):
                            await browser.close()
                            return href
                    # Try obvious anchors
                    link = page.locator('a[href$=".pdf"]')
                    if await link.count():
                        href = await link.first.get_attribute("href")
                        await browser.close()
                        return href
                    # Try button that opens PDF in new tab
                    # Fallback: look for any link containing 'pdf'
                    any_pdf = page.locator('a:has-text("PDF")')
                    if await any_pdf.count():
                        href = await any_pdf.first.get_attribute("href")
                        await browser.close()
                        return href
                    await browser.close()
            return None
        except Exception as e:
            print(f"[PLAYWRIGHT] Failed to resolve PDF from {url}: {e}")
            return None

    async def _extract_abstract_with_playwright(self, url: str) -> Optional[str]:
        if not url:
            return None
        try:
            from playwright.async_api import async_playwright  # type: ignore
        except Exception:
            return None
        try:
            async with self._sem:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    context = await browser.new_context()
                    page = await context.new_page()
                    await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                    # Common meta
                    sel = 'meta[name="citation_abstract"], meta[name="dc.description"], meta[name="description"]'
                    loc = page.locator(sel)
                    if await loc.count():
                        content = await loc.first.get_attribute("content")
                        await browser.close()
                        return content
                    # Try visible abstract blocks
                    text = await page.locator('section:has-text("Abstract")').first.inner_text()
                    if text:
                        await browser.close()
                        return text
                    await browser.close()
            return None
        except Exception:
            return None

    def _select_pdf_url(self, d: Dict[str, Any]) -> Optional[str]:
        # Prefer Unpaywall OA link
        oa_pdf = (d.get("links") or {}).get("oa_pdf")
        if oa_pdf and ".pdf" in oa_pdf.lower():
            return oa_pdf
        # arXiv direct pdf
        url = d.get("url") or ""
        if "arxiv.org/pdf" in url:
            return url
        # CORE downloadUrl (may be direct pdf)
        if d.get("source") == "core" and url:
            return url
        return None

    async def _download_and_extract_pdf_text(self, session: aiohttp.ClientSession, pdf_url: str) -> Optional[str]:
        try:
            async with self._sem:
                async with session.get(pdf_url, headers={"User-Agent": "Waga-Academy-Extractor/1.0"}) as resp:
                    if resp.status != 200:
                        return None
                    ctype = resp.headers.get("Content-Type", "").lower()
                    if "pdf" not in ctype and not pdf_url.lower().endswith(".pdf"):
                        return None
                    raw = await resp.read()
            from io import BytesIO
            bio = BytesIO(raw)
            import PyPDF2
            reader = PyPDF2.PdfReader(bio)
            pages = []
            for p in reader.pages:
                try:
                    pages.append(p.extract_text() or "")
                except Exception:
                    pages.append("")
            text = "\n\n".join([t.strip() for t in pages if t and t.strip()])
            return text.strip() or None
        except Exception as e:
            print(f"[PDF] Failed to extract PDF {pdf_url}: {e}")
            return None

    def _simple_chunk(self, text: str, chunk_size: int = 2000, overlap: int = 200) -> List[str]:
        chunks: List[str] = []
        if not text:
            return chunks
        start = 0
        n = len(text)
        while start < n:
            end = min(n, start + chunk_size)
            chunks.append(text[start:end])
            if end == n:
                break
            start = max(end - overlap, start + 1)
        return chunks 