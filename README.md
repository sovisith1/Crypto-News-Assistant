# Crypto-News-Assistant

A smart Python-based command-line assistant that delivers up-to-date, AI-powered insights about major cryptocurrencies. Users select a coin and a relevant market question, and the tool fetches recent news headlines using NewsAPI, then summarizes the news using OpenAI GPT-4 for instant understanding of market trends.

Features:
• Choose from 5 top coins: Bitcoin, Ethereum, Solana, Dogecoin, Cardano
• Answer 3 key market questions (e.g., price drivers, red flags, scaling plans)
• Fetches real-time headlines via NewsAPI
• Summarizes news using OpenAI GPT-4 or GPT-3.5
• Clean CLI design with error handling and session logging to CSV

Tech Stack
• Python 3
• openai, requests, csv, json, dotenv

Example output:
Select a coin:
1. Bitcoin
2. Ethereum
...

Select a question:
1. What’s driving the price movement?
...

Summary:
“Ethereum’s recent surge is linked to the upcoming Dencun upgrade, strong investor confidence, and increased Layer 2 activity...”
