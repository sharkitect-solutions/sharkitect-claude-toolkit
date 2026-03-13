---
name: agents-llamaindex
description: "Use when building LLM applications with LlamaIndex: RAG pipelines, document ingestion, vector index construction, query engine configuration, or agentic retrieval. Also use when choosing between LlamaIndex index types, debugging retrieval quality, implementing advanced RAG patterns (hybrid search, reranking, routing), or selecting chunking strategies. NEVER use for LangChain-specific patterns or architecture, general prompt engineering without retrieval, non-LLM data pipelines, or vector database administration without LlamaIndex."
version: "2.0"
optimized: true
optimized_date: "2026-03-12"
---

# LlamaIndex - Data Framework for LLM Applications

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Index type selection, chunking strategy, RAG architecture patterns, query mode selection, retrieval debugging, common failures, anti-patterns | Always (auto-loaded) |
| references/query_engines.md | Query engine modes (compact, tree_summarize, refine, accumulate), streaming configuration, custom prompt templates, response synthesis internals | When configuring query engines beyond defaults, debugging response quality issues, or choosing between response synthesis modes |
| references/agents.md | FunctionAgent setup, tool wrapping (QueryEngineTool), multi-step reasoning, agent-based RAG with tool selection | When building agentic RAG applications that combine document retrieval with custom tools or multi-step reasoning |
| references/data_connectors.md | Data connector catalog (SimpleDirectoryReader, web readers, database readers, API readers), custom loader patterns, metadata attachment | When ingesting data from non-trivial sources, building custom loaders, or troubleshooting document loading issues |

Do NOT load companion files for basic VectorStoreIndex creation, simple query engine usage, or standard document loading -- SKILL.md covers these decisions fully.

## Scope Boundary

| Area | This Skill | Other Skill |
|---|---|---|
| RAG pipeline architecture with LlamaIndex | YES | -- |
| Index type selection and configuration | YES | -- |
| Chunking and node parsing strategy | YES | -- |
| Query engine and retriever configuration | YES | -- |
| LlamaIndex agent setup with tools | YES | -- |
| Retrieval quality debugging | YES | -- |
| Vector store integration via LlamaIndex | YES | -- |
| LangChain architecture and patterns | NO | agents-crewai or general LLM |
| Pure vector database administration | NO | database tooling |
| Prompt engineering without retrieval | NO | prompt-engineering-guidance |
| ML model training and evaluation | NO | data science tooling |
| A/B testing RAG quality | NO | ab-test-setup |

## Index Type Decision Matrix

| Data Characteristic | Best Index | Why | Gotcha |
|---|---|---|---|
| Unstructured text, need semantic search | VectorStoreIndex | Embedding-based similarity is the default RAG pattern | Embedding model choice affects quality more than index type -- text-embedding-3-small vs ada-002 is a 15-20% retrieval quality gap |
| Need to process ALL documents (summarization) | SummaryIndex (formerly ListIndex) | Scans every node sequentially, no information loss | O(n) cost -- every query touches every node. Only viable for <100 docs or when completeness matters more than speed |
| Hierarchical document structure (books, manuals) | TreeIndex | Builds summary tree, queries traverse top-down | Tree depth affects latency. Default num_children=10 works for most cases. Deeper trees = more LLM calls per query |
| Structured relationships between entities | KnowledgeGraphIndex | Extracts and queries entity-relationship triples | Extraction quality varies wildly. GPT-4 extracts better triples than GPT-3.5. Manual triple validation recommended for production |
| Mixed query types on same data | ComposableGraph (multi-index) | Routes queries to appropriate sub-index | Index composition adds routing latency (~200-500ms). Only justified when data genuinely needs different access patterns |
| Tabular or SQL-queryable data | SQLTableIndex / PandasQueryEngine | Translates natural language to SQL/pandas | LLM-generated SQL is unreliable for complex joins. Always sandbox SQL execution. PandasQueryEngine runs arbitrary Python -- security risk |

**Default recommendation**: Start with VectorStoreIndex. Switch only when retrieval quality plateaus and you've already optimized chunking and embedding model.

## Chunking Strategy Guide

| Strategy | Chunk Size | Overlap | Best For | Retrieval Impact |
|---|---|---|---|---|
| Fixed token chunking | 512-1024 tokens | 50-100 tokens | General-purpose, predictable behavior | Baseline. Simple but splits mid-sentence/paragraph |
| Sentence-based chunking | Variable (SentenceSplitter) | 1-2 sentences | Conversational content, Q&A docs | Better semantic boundaries. Default SentenceSplitter with chunk_size=1024 is the best starting point |
| Semantic chunking | Variable (SemanticSplitterNodeParser) | Adaptive by embedding similarity | Technical documentation with topic shifts | Groups semantically similar sentences. Requires extra embedding calls during indexing (2-3x cost). Worth it for heterogeneous docs |
| Hierarchical chunking (HierarchicalNodeParser) | Multiple levels (2048/512/128) | Per-level | Long documents needing both overview and detail retrieval | Enables auto-merging retrieval. Most complex setup but best quality for long-form content |

**Critical gotchas**:
- Chunk size > context window of embedding model = silent truncation. text-embedding-3-small handles 8191 tokens; ada-002 handles 8191; many open-source models cap at 512
- Overlap too large (>20% of chunk) wastes tokens and adds noise. 50-100 tokens is the sweet spot
- Metadata counts toward chunk token budget in LlamaIndex. Documents with rich metadata may need larger chunk_size to preserve content

## RAG Architecture Decision

| Pattern | When to Use | LlamaIndex Implementation | Quality vs Naive RAG |
|---|---|---|---|
| Naive RAG (embed + retrieve + generate) | Prototyping, simple Q&A, homogeneous documents | VectorStoreIndex + as_query_engine() | Baseline |
| Sentence-window retrieval | Need surrounding context for retrieved sentences | SentenceWindowNodeParser + MetadataReplacementPostProcessor | +15-25% answer quality on long documents |
| Auto-merging retrieval | Hierarchical docs, need to "zoom out" when multiple child chunks are relevant | HierarchicalNodeParser + AutoMergingRetriever | +10-20% on structured documents, minimal gain on flat text |
| Hybrid search (vector + keyword) | Technical content with domain-specific terminology that embeddings miss | VectorStoreIndex + BM25Retriever via QueryFusionRetriever | +10-30% on technical/domain-specific queries |
| Reranking | High-recall retrieval needed, willing to trade latency for precision | Retrieve top_k=20, rerank to top_k=3 with CohereRerank or SentenceTransformerRerank | +15-25% precision. Adds 200-500ms latency per query |
| Router-based | Multiple document collections with different query patterns | RouterQueryEngine with selector (LLM or embedding-based) | Depends on routing accuracy. LLMSingleSelector ~85-90% correct routing |
| Agentic RAG | Complex multi-step questions, need tool use alongside retrieval | FunctionAgent with QueryEngineTool | Best for complex reasoning. 3-8x latency of naive RAG |

**Progression path**: Naive RAG -> add reranking -> add hybrid search -> switch to sentence-window or auto-merging if document length is the bottleneck.

## Query Engine Mode Selection

| Response Mode | Behavior | Token Cost | Best For |
|---|---|---|---|
| `compact` (default) | Stuffs as many chunks as fit into one LLM call, then synthesizes | Low (1 LLM call) | Most queries. Start here |
| `refine` | Iterates through each chunk, refining the answer progressively | High (1 call per chunk) | When every chunk matters and you need comprehensive answers |
| `tree_summarize` | Recursively summarizes chunks in a tree structure | Medium (log(n) calls) | Summarization tasks over many chunks |
| `simple_summarize` | Truncates to fit context, single LLM call | Lowest | Quick summaries where completeness isn't critical |
| `accumulate` | Generates response per chunk, concatenates | High (1 call per chunk) | When you want per-source answers (comparison, multi-perspective) |
| `no_text` | Returns retrieved nodes without LLM synthesis | Zero | Retrieval-only use cases, custom downstream processing |

## Common RAG Failure Modes

| Failure | Symptoms | Root Cause | Fix |
|---|---|---|---|
| Retrieval miss (relevant doc not retrieved) | Correct answer exists in corpus but response says "I don't know" | Embedding similarity doesn't capture the query-document relationship | Increase top_k, add hybrid search (BM25), try different embedding model, improve chunking boundaries |
| Context window overflow | Truncated or incomplete answers | Too many or too large chunks stuffed into prompt | Reduce top_k, reduce chunk_size, use reranking to filter low-quality retrievals |
| Cross-chunk information loss | Answer requires info split across chunk boundary | Fixed chunking split a key paragraph | Increase overlap, use sentence-window retrieval, or switch to semantic chunking |
| Hallucination despite retrieval | Plausible but wrong answer with sources that don't support it | LLM ignores retrieved context or extrapolates beyond it | Use stricter system prompt ("answer ONLY from provided context"), reduce temperature, add faithfulness evaluation |
| Stale index | Answers reflect old information | Index not rebuilt after source documents changed | Implement incremental indexing with document hashing, or use refresh_ref_docs() for VectorStoreIndex |
| Metadata filtering miss | Query about specific document type returns results from all types | Metadata not attached during indexing, or filter not applied at query time | Attach metadata during ingestion, use MetadataFilters at query time |

## LlamaIndex-Specific Gotchas

| Gotcha | Impact | Fix |
|---|---|---|
| `Settings` is global state | Changing Settings.llm in one query affects ALL subsequent queries in the same process | Pass llm/embed_model explicitly per-query: `index.as_query_engine(llm=specific_llm)` |
| ServiceContext is deprecated (v0.10+) | Old tutorials using ServiceContext will break | Use `Settings` global or pass parameters directly. ServiceContext still works but logs deprecation warnings |
| Default embedding model requires OpenAI key | VectorStoreIndex.from_documents() fails without OPENAI_API_KEY even if using Anthropic for LLM | Set `Settings.embed_model` explicitly before indexing. Use HuggingFaceEmbedding for local embedding |
| Persist/load loses custom settings | Loading an index from disk doesn't restore the LLM/embedding model used during creation | Set Settings before calling load_index_from_storage(), or pass service_context explicitly |
| Async support is partial | Some components support async (aquery), others block | Check component docs. VectorStoreIndex supports async retrieval. Not all response synthesizers do |
| CallbackManager overhead | Token counting and event logging add 5-10% latency | Disable in production: `Settings.callback_manager = CallbackManager()` |
| LlamaHub connectors vary in quality | Some connectors are community-maintained with sparse error handling | Test connectors thoroughly before production. SimpleDirectoryReader is the most battle-tested |

## Anti-Patterns

| Name | Pattern | Why It Fails | Fix |
|---|---|---|---|
| The Chunk Dump | Default chunk_size with no overlap on heterogeneous documents | Key information split at arbitrary boundaries. Retrieved chunks lack context. Answers miss obvious information | Analyze document structure first. Use SentenceSplitter with overlap. Consider semantic chunking for topic-diverse corpora |
| The Kitchen Sink Index | One VectorStoreIndex for all document types (PDFs, code, tables, chat logs) | Embedding space becomes noisy. Code similarity != text similarity. Retrieval quality degrades for all types | Separate indices per document type. Use RouterQueryEngine to route queries to appropriate index |
| The Top-1 Gambler | similarity_top_k=1 to "keep it focused" | Single chunk rarely contains full answer. No redundancy if the top result is wrong. Reranking impossible | Start with top_k=5, add reranking. Reduce only after measuring retrieval quality |
| The Embed-and-Pray | Skip evaluation, assume retrieval works because "embeddings are good" | No visibility into retrieval quality. Gradual degradation as corpus grows. Users report bad answers but you can't diagnose | Implement retrieval evaluation (HitRate, MRR) on a labeled query set. Use LlamaIndex's RetrieverEvaluator |
| The Monolithic Prompt | Stuff all instructions, context, and query into one massive prompt template | Context competes with instructions for attention. Response quality drops as context grows. Difficult to debug which part failed | Separate system prompt from context. Use response_mode="compact" or "refine". Keep instructions concise |
| The Rebuild Loop | Rebuilding entire index on every document update | O(n) embedding cost on every change. Expensive and slow as corpus grows | Use VectorStoreIndex.insert() for new docs, delete_ref_doc() + insert for updates. Or use external vector store with upsert |

## Rationalization Table

| Rationalization | Why It Fails |
|---|---|
| "Embeddings capture all meaning, no need for keyword search" | Embeddings miss exact terminology, acronyms, and domain jargon. Hybrid search (vector + BM25) consistently outperforms pure vector on technical content |
| "More chunks in context = better answers" | Beyond 5-8 chunks, LLM attention degrades ("lost in the middle" problem). Quality peaks at a sweet spot, then declines |
| "We'll optimize retrieval later, just ship the prototype" | RAG quality is retrieval quality. A prototype with bad retrieval teaches users the system is unreliable. First impressions are hard to reverse |
| "One big index is simpler than multiple small ones" | Simplicity in architecture creates complexity in debugging. When retrieval fails, you can't isolate whether the problem is embedding, chunking, or corpus noise |
| "LlamaIndex handles everything, we don't need to understand the internals" | LlamaIndex is a framework, not magic. Default settings work for demos. Production quality requires understanding embedding models, chunking strategies, and retrieval patterns |

## Red Flags

- Using default chunk_size without testing alternatives on actual queries -- even 512 vs 1024 can shift retrieval quality by 10-20%
- No retrieval evaluation metrics (HitRate, MRR) in the development process -- you're flying blind on the most critical component
- VectorStoreIndex with top_k=1 -- single-chunk retrieval has no redundancy and no reranking opportunity
- Mixing document types (code, text, tables) in one index without routing -- embedding spaces for different content types don't mix well
- Using response_mode="refine" on 20+ chunks -- O(n) LLM calls, high latency, diminishing quality returns
- No hybrid search on technical/domain-specific content -- embeddings consistently miss exact terminology matches
- Building RAG without a test query set -- impossible to measure improvement or detect regression
- Loading index from disk without verifying Settings match the creation-time configuration

## NEVER

- Build a production RAG system without a labeled evaluation set -- retrieval quality is unmeasurable without ground-truth queries
- Use SQLTableIndex or PandasQueryEngine in untrusted environments -- LLM-generated SQL/Python executes arbitrary code
- Skip chunking strategy analysis -- the default is rarely optimal for any specific document corpus
- Assume embedding model quality is interchangeable -- text-embedding-3-small, ada-002, and open-source models have significant retrieval quality differences on the same corpus
- Use global Settings for multi-tenant applications -- shared state means one user's configuration affects another's queries
