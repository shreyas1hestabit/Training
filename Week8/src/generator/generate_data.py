import json
import random
import os

def generate_finance_dataset(count=1300):
    companies = ["Apple", "Tesla", "NVIDIA", "Microsoft", "Goldman Sachs", "Amazon", "JPMorgan", "Visa"]
    sectors = ["Tech", "Energy", "Banking", "Retail", "Healthcare"]
    currencies = ["USD", "EUR", "GBP", "JPY", "INR"]

    dataset = []

    for i in range(count):
        # Determine category based on index to ensure balance
        if i % 3 == 0:  # 1. QA (Financial Definitions)
            terms = {
                "EBITDA": "Earnings Before Interest, Taxes, Depreciation, and Amortization.",
                "Short Selling": "Selling a security you do not own, expecting the price to fall.",
                "Dividend Yield": "The ratio of a company's annual dividend compared to its share price.",
                "Market Cap": "The total value of a company's shares on the stock market."
            }
            term, definition = random.choice(list(terms.items()))
            item = {
                "instruction": f"Explain the financial term: {term}",
                "input": "",
                "output": f"{term} stands for {definition} It is a key metric for investors to evaluate {random.choice(sectors)} companies."
            }

        elif i % 3 == 1:  # 2. Reasoning (Calculations)
            rev = random.randint(100, 1000)
            exp = random.randint(50, int(rev * 0.8))
            margin = round(((rev - exp) / rev) * 100, 2)
            item = {
                "instruction": "Calculate the Net Profit Margin based on the provided data.",
                "input": f"Company: {random.choice(companies)}. Revenue: ${rev}M. Total Expenses: ${exp}M.",
                "output": f"Step 1: Subtract expenses from revenue (${rev}M - ${exp}M = ${rev-exp}M Net Income).\nStep 2: Divide Net Income by Revenue (${rev-exp}M / ${rev}M = {round(margin/100, 4)}).\nStep 3: Convert to percentage. The Profit Margin is {margin}%."
            }

        else:  # 3. Extraction (Data Mining)
            prices = [150.25, 2400.10, 45.30, 190.00]
            price = random.choice(prices)
            pct = round(random.uniform(0.5, 5.0), 2)
            item = {
                "instruction": "Extract the ticker symbol and the stock price change from the headline.",
                "input": f"News: {random.choice(companies)} shares rose {pct}% to close at ${price} today.",
                "output": f"Ticker: {random.choice(companies)[:3].upper()}, Price Change: +{pct}%."
            }
        
        dataset.append(item)

    # Save to JSONL
    os.makedirs('src/data', exist_ok=True)
    with open('src/data/raw_train.jsonl', 'w') as f:
        for entry in dataset:
            f.write(json.dumps(entry) + '\n')
    
    print(f" Generated {count} samples in src/data/raw_train.jsonl")

if __name__ == "__main__":
    generate_finance_dataset(1300)