"""
Example usage of Multi-Agent System with multiple Azure indexes.
Demonstrates how to query both Reddit and Play Store indexes.
All outputs are saved to the 'output' folder.
Updated to export ALL entries from each Azure Cognitive Search index.
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from nemotron_client import NemotronClient
from vector_db import SocialMediaVectorDB
from agentic_rag import AgenticRAG
from multi_agent_system import MultiAgentSystem
import json
from collections import Counter, defaultdict


def ensure_output_folder():
    """Create output folder if it doesn't exist."""
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"? Created output folder: {output_dir}")
    return output_dir


def save_to_file(filename, content, output_dir="output"):
    """Save content to a file in the output directory."""
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"?? Saved: {filepath}")
    return filepath


def export_all_documents(search_client, index_type: str, timestamp: str, output_dir: str, max_per_page: int = 1000) -> str:
    """Export all documents from an Azure Cognitive Search index to a JSONL file.
    Uses server-side paging via continuation tokens.
    Returns path to exported file and also returns list of docs.
    """
    filename = f"all_{index_type}_documents_{timestamp}.jsonl"
    path = os.path.join(output_dir, filename)
    exported = 0
    all_docs = []
    with open(path, "w", encoding="utf-8") as f:
        # Initial search (empty search_text to fetch all)
        results = search_client.search(search_text="*", top=max_per_page)
        for doc in results:
            json.dump(doc, f)
            f.write("\n")
            exported += 1
            all_docs.append(doc)
        # Handle continuation pages if available
        while hasattr(results, "get_continuation_token"):
            token = results.get_continuation_token()
            if not token:
                break
            results = search_client.search(search_text="*", top=max_per_page, continuation_token=token)
            for doc in results:
                json.dump(doc, f)
                f.write("\n")
                exported += 1
                all_docs.append(doc)
    return path, all_docs, exported


def summarize_documents(index_type: str, docs: list) -> str:
    """Generate a human-readable summary of all documents collected from an index."""
    if not docs:
        return f"No documents found in {index_type} index."
    lines = [f"Summary for {index_type} index", "=" * 60, f"Total Documents: {len(docs)}"]
    # Common fields
    sentiments = Counter()
    categories = Counter()
    dates = Counter()
    extra_fields = defaultdict(Counter)
    rating_counter = Counter()
    score_counter = Counter()
    app_counter = Counter()
    subreddit_counter = Counter()

    for d in docs:
        sentiments[str(d.get('sentiment',''))] += 1
        categories[str(d.get('category',''))] += 1
        dates[str(d.get('date',''))] += 1
        if index_type == 'playstore':
            app_counter[str(d.get('app_name',''))] += 1
            if 'rating' in d and d.get('rating') is not None:
                rating_counter[int(d.get('rating'))] += 1
        if index_type == 'reddit':
            subreddit_counter[str(d.get('subreddit',''))] += 1
            if 'score' in d and d.get('score') is not None:
                score_counter[int(d.get('score'))] += 1

    lines.append("\nTop Sentiments:")
    for k,v in sentiments.most_common():
        if k:
            lines.append(f"  {k}: {v}")
    lines.append("\nTop Categories:")
    for k,v in categories.most_common(15):
        if k:
            lines.append(f"  {k}: {v}")

    if index_type == 'playstore':
        lines.append("\nTop Apps:")
        for k,v in app_counter.most_common():
            if k:
                lines.append(f"  {k}: {v}")
        lines.append("\nRatings Distribution:")
        for r in sorted(rating_counter.keys(), reverse=True):
            lines.append(f"  {r} stars: {rating_counter[r]}")
    elif index_type == 'reddit':
        lines.append("\nSubreddit Distribution:")
        for k,v in subreddit_counter.most_common():
            if k:
                lines.append(f"  {k}: {v}")
        # Score distribution buckets
        score_buckets = {"<=0":0, "1-10":0, "11-50":0, ">50":0}
        for s,count in score_counter.items():
            if s <= 0:
                score_buckets['<=0'] += 1
            elif s <= 10:
                score_buckets['1-10'] += 1
            elif s <= 50:
                score_buckets['11-50'] += 1
            else:
                score_buckets['>50'] += 1
        lines.append("\nScore Buckets:")
        for k,v in score_buckets.items():
            lines.append(f"  {k}: {v}")

    lines.append("\nDate Span:")
    non_empty_dates = [d for d in dates.keys() if d and d.lower() != 'none']
    if non_empty_dates:
        lines.append(f"  Earliest: {min(non_empty_dates)}")
        lines.append(f"  Latest: {max(non_empty_dates)}")
    else:
        lines.append("  No valid dates")

    return "\n".join(lines)


def main():
    # Load environment variables
    load_dotenv()
    
    # Create output folder
    output_dir = ensure_output_folder()
    
    # Create a timestamp for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create a master log file
    log_file = os.path.join(output_dir, f"run_log_{timestamp}.txt")
    
    def log_and_print(message):
        """Print and log to file."""
        print(message)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(message + "\n")
    
    log_and_print("=" * 80)
    log_and_print("Multi-Agent System with Multiple Azure Indexes - Example")
    log_and_print("=" * 80)
    log_and_print(f"Run Timestamp: {timestamp}")
    log_and_print(f"Output Directory: {output_dir}")
    
    # Initialize Nemotron client
    log_and_print("\n?? Initializing Nemotron client...")
    nvidia_api_key = os.getenv("NVIDIA_API_KEY")
    if not nvidia_api_key:
        log_and_print("? NVIDIA_API_KEY not found. Please set it in your .env file.")
        return
    
    nemotron = NemotronClient(api_key=nvidia_api_key)
    log_and_print("? Nemotron client initialized")
    
    # Initialize Azure Cognitive Search databases
    log_and_print("\n?? Initializing Azure Cognitive Search indexes...")
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    api_key = os.getenv("AZURE_SEARCH_API_KEY")
    
    if not endpoint or not api_key:
        log_and_print("? Azure Search credentials not found. Please set them in your .env file.")
        return
    
    # Initialize both indexes
    vector_dbs = {}
    
    try:
        reddit_db = SocialMediaVectorDB(
            endpoint=endpoint,
            api_key=api_key,
            index_type="reddit"
        )
        vector_dbs['reddit'] = reddit_db
        log_and_print("? Reddit index initialized (tmobile-reddit-posts)")
    except Exception as e:
        log_and_print(f"?? Reddit index not available: {e}")
    
    try:
        playstore_db = SocialMediaVectorDB(
            endpoint=endpoint,
            api_key=api_key,
            index_type="playstore"
        )
        vector_dbs['playstore'] = playstore_db
        log_and_print("? Play Store index initialized (tmobile-playstore-reviews)")
    except Exception as e:
        log_and_print(f"?? Play Store index not available: {e}")
    
    if not vector_dbs:
        log_and_print("? No indexes available. Please run data collection scripts first:")
        log_and_print("   python collect_reddit.py")
        log_and_print("   python collect_playstore.py")
        return

    # METHOD 0: Export ALL raw documents from each index
    log_and_print("\n" + "=" * 80)
    log_and_print("METHOD 0: Export ALL documents from each index")
    log_and_print("=" * 80)

    exported_info = []
    for key, db in vector_dbs.items():
        log_and_print(f"\n?? Exporting all documents from {key} index...")
        try:
            path, docs, count = export_all_documents(db.search_client, key, timestamp, output_dir)
            log_and_print(f"? Export complete: {count} documents written to {os.path.basename(path)}")
            # Summarize
            summary = summarize_documents(key, docs)
            summary_file = f"summary_{key}_index_{timestamp}.txt"
            save_to_file(summary_file, summary, output_dir)
            exported_info.append((key, count, path, summary_file))
        except Exception as e:
            log_and_print(f"? Failed exporting {key} index: {e}")

    # METHOD 1: Using AgenticRAG directly
    log_and_print("\n" + "=" * 80)
    log_and_print("METHOD 1: Using AgenticRAG with Multiple Indexes")
    log_and_print("=" * 80)
    
    agentic_rag = AgenticRAG(nemotron, vector_dbs)
    
    # Example query that could use multiple platforms
    query1 = "What are the main complaints about the T-Mobile app?"
    log_and_print(f"\n?? Query: {query1}")
    log_and_print("\n?? AgenticRAG Response:")
    response1 = agentic_rag.query(query1)
    log_and_print(response1)
    
    save_to_file(
        f"method1_query1_app_complaints_{timestamp}.txt",
        f"QUERY: {query1}\n\n{'=' * 80}\n\nRESPONSE:\n\n{response1}",
        output_dir
    )
    
    query2 = "What network issues are people discussing on Reddit?"
    log_and_print(f"\n\n?? Query: {query2}")
    log_and_print("\n?? AgenticRAG Response:")
    response2 = agentic_rag.query(query2)
    log_and_print(response2)
    
    save_to_file(
        f"method1_query2_network_issues_{timestamp}.txt",
        f"QUERY: {query2}\n\n{'=' * 80}\n\nRESPONSE:\n\n{response2}",
        output_dir
    )
    
    # METHOD 2: Using Multi-Agent System for comprehensive reports
    log_and_print("\n\n" + "=" * 80)
    log_and_print("METHOD 2: Using Multi-Agent System for Comprehensive Analysis")
    log_and_print("=" * 80)
    
    multi_agent = MultiAgentSystem(nemotron, agentic_rag)
    report_query = "Analyze all complaints about billing and pricing"
    log_and_print(f"\n?? Report Query: {report_query}\n")
    report = multi_agent.generate_report(report_query, verbose=True)
    
    log_and_print("\n" + "=" * 80)
    log_and_print("?? FINAL REPORT")
    log_and_print("=" * 80)
    log_and_print(report['final_report'])
    
    report_content = f"""MULTI-AGENT REPORT: Billing and Pricing Analysis
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Query: {report_query}

{'=' * 80}
RESEARCH SUMMARY
{'=' * 80}

{report['research_summary']}

{'=' * 80}
OUTLINE
{'=' * 80}

{report['outline']}

{'=' * 80}
DRAFT
{'=' * 80}

{report['draft']}

{'=' * 80}
FINAL REPORT
{'=' * 80}

{report['final_report']}
"""
    save_to_file(f"method2_billing_report_full_{timestamp}.txt", report_content, output_dir)
    save_to_file(f"method2_billing_01_research_{timestamp}.txt", report['research_summary'], output_dir)
    save_to_file(f"method2_billing_02_outline_{timestamp}.txt", report['outline'], output_dir)
    save_to_file(f"method2_billing_03_draft_{timestamp}.txt", report['draft'], output_dir)
    save_to_file(f"method2_billing_04_final_{timestamp}.txt", report['final_report'], output_dir)
    
    # METHOD 3: Auto-initialization (simplest method)
    log_and_print("\n\n" + "=" * 80)
    log_and_print("METHOD 3: Auto-Initialization from Environment Variables")
    log_and_print("=" * 80)
    auto_multi_agent = MultiAgentSystem(nemotron)
    log_and_print("\n? Multi-agent system auto-initialized from environment variables")
    quick_query = "What are users saying about customer service?"
    log_and_print(f"\n?? Quick Query: {quick_query}\n")
    quick_report = auto_multi_agent.generate_report(quick_query, verbose=True)
    log_and_print("\n" + "=" * 80)
    log_and_print("?? QUICK REPORT")
    log_and_print("=" * 80)
    log_and_print(quick_report['final_report'])
    quick_report_content = f"""QUICK REPORT: Customer Service Analysis
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Query: {quick_query}

{'=' * 80}
RESEARCH SUMMARY
{'=' * 80}

{quick_report['research_summary']}

{'=' * 80}
OUTLINE
{'=' * 80}

{quick_report['outline']}

{'=' * 80}
FINAL REPORT
{'=' * 80}

{quick_report['final_report']}
"""
    save_to_file(f"method3_customer_service_report_{timestamp}.txt", quick_report_content, output_dir)
    
    # Create summary index file with export section
    exported_section_lines = ["METHOD 0 - Raw Index Exports:"]
    for idx, count, path, summary_file in exported_info:
        exported_section_lines.append(f"  - {idx}: {count} documents (file: {os.path.basename(path)}, summary: {summary_file})")
    exported_section = "\n".join(exported_section_lines)
    summary_content = f"""Multi-Agent System Run Summary
{'=' * 80}
Run Timestamp: {timestamp}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

AVAILABLE INDEXES:
{', '.join(vector_dbs.keys())}

FILES GENERATED:
{'=' * 80}

{exported_section}

METHOD 1 - AgenticRAG Direct Queries:
  1. method1_query1_app_complaints_{timestamp}.txt (Query: "{query1}")
  2. method1_query2_network_issues_{timestamp}.txt (Query: "{query2}")

METHOD 2 - Comprehensive Multi-Agent Report:
  3. method2_billing_report_full_{timestamp}.txt (Complete report)
  4. method2_billing_01_research_{timestamp}.txt (Research stage)
  5. method2_billing_02_outline_{timestamp}.txt (Outline stage)
  6. method2_billing_03_draft_{timestamp}.txt (Draft stage)
  7. method2_billing_04_final_{timestamp}.txt (Final stage) (Query: "{report_query}")

METHOD 3 - Auto-Initialized Quick Report:
  8. method3_customer_service_report_{timestamp}.txt (Query: "{quick_query}")

LOG FILE:
  9. run_log_{timestamp}.txt (Complete execution log)

{'=' * 80}
Raw exports are JSONL (one document per line). Summaries contain aggregate statistics.
To view any report or dataset, open the corresponding file in the output folder.
"""
    save_to_file(f"SUMMARY_{timestamp}.txt", summary_content, output_dir)
    
    log_and_print("\n" + "=" * 80)
    log_and_print("? ALL OUTPUTS (INCLUDING FULL INDEX EXPORTS) SAVED TO OUTPUT FOLDER")
    log_and_print("=" * 80)
    log_and_print(f"\nOutput Location: {os.path.abspath(output_dir)}")
    log_and_print(f"Summary File: SUMMARY_{timestamp}.txt")
    log_and_print(f"Log File: run_log_{timestamp}.txt")
    log_and_print("\nGenerated Files include raw exports, summaries, and multi-agent reports.")


if __name__ == "__main__":
    main()
