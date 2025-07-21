#!/usr/bin/env python3
"""
Crypto News Assistant
---------------------
• Menu of 5 coins
• 3 fixed questions per coin
• Pull 5 fresh headlines (NewsAPI)
• Ask GPT-4 (or GPT-3.5) for a short answer
• Display answer and log the session
"""

import csv
import datetime as dt
import json
import sys
from pathlib import Path

import requests
import openai
from openai import OpenAIError, RateLimitError   # v1.x import style

# ----------------- CONFIG ----------------- #
NEWS_API_KEY   = "Insert NewsAPI key"      # insert your NewsAPI key
OPENAI_API_KEY = "Insert OpenAI API Key"   # insert your OpenAI key
openai.api_key = OPENAI_API_KEY

GPT_MODEL = "gpt-4o"                # change to gpt-3.5-turbo if needed
HEADLINE_COUNT = 5

NEWS_URL = "https://newsapi.org/v2/everything"
COINS = ["Bitcoin", "Ethereum", "Solana", "Dogecoin", "Cardano"]
QUESTIONS = [
    "What’s driving the price movement of {coin}?",
    "Are there any red flags about {coin} right now?",
    "Has {coin} announced anything about scaling or security improvements?"
]
LOG_FILE = Path("log.csv")
# ------------------------------------------ #

def fetch_headlines(coin: str, limit: int = 5) -> list[str]:
    """Return recent news headlines or [] if the request fails."""
    params = {
        "q": coin,
        "language": "en",
        "pageSize": limit,
        "sortBy": "publishedAt",
        "apiKey": NEWS_API_KEY
    }
    try:
        r = requests.get(NEWS_URL, params=params, timeout=15)
        r.raise_for_status()
        articles = r.json().get("articles", [])
        return [a["title"] for a in articles][:limit]
    except (requests.RequestException, json.JSONDecodeError) as exc:
        print(f"News API error: {exc}")
        return []

def ask_gpt(question: str, headlines: list[str]) -> str:
    """
    Ask GPT and return a summary string.
    Handles quota and rate-limit errors gracefully.
    """
    system_msg = (
        "You are a concise crypto news assistant. "
        "Answer the user's question using ONLY the context of the provided headlines. "
        "If the headlines lack relevant information, say so."
    )
    user_msg = f"Question: {question}\n\nHeadlines:\n" + \
               "\n".join(f"- {h}" for h in headlines)

    try:
        resp = openai.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user",   "content": user_msg}
            ],
            max_tokens=250,
            temperature=0.7
        )
        return resp.choices[0].message.content.strip()

    except RateLimitError:
        return ("OpenAI rate-limit or quota error. "
                "Check your API billing or wait for limits to reset.")

    except OpenAIError as exc:
        return f"OpenAI API error: {exc}"

def log_interaction(date: str, coin: str, qnum: int, summary: str):
    """Append (or create) log.csv."""
    new_file = not LOG_FILE.exists()
    with LOG_FILE.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["date", "coin", "question_number", "summary"])
        w.writerow([date, coin, qnum, summary])

def prompt_menu(title: str, options: list[str]) -> int:
    """Simple numbered menu, returns 1-based selection."""
    print(f"\n{title}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        try:
            choice = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            sys.exit(0)
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return int(choice)
        print("Invalid choice, try again.")

def main():
    # 1. coin selection
    c_idx = prompt_menu("Select a coin:", COINS)
    coin = COINS[c_idx - 1]

    # 2. question selection
    qs = [q.format(coin=coin) for q in QUESTIONS]
    q_idx = prompt_menu(f"Select a question about {coin}:", qs)
    question = qs[q_idx - 1]

    # 3. fetch headlines
    print(f"\nFetching {HEADLINE_COUNT} recent headlines about {coin}…")
    headlines = fetch_headlines(coin, HEADLINE_COUNT)
    if not headlines:
        print("No headlines found or API request failed.")
        return

    # 4. ask GPT
    print("Asking GPT, please wait…")
    summary = ask_gpt(question, headlines)

    # 5. display answer
    print("\n" + "-"*60)
    print(f"{coin} — {question}")
    print("-"*60)
    print(summary)
    print("-"*60)

    # 6. log the session
    try:
        log_interaction(dt.datetime.now().isoformat(timespec="seconds"),
                        coin, q_idx, summary)
    except IOError as exc:
        print(f"Could not write log file: {exc}")

if __name__ == "__main__":
    main()