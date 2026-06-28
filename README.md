# Amazon Product Scraper

A lightweight, robust Python script that dynamically scrapes product information from Amazon search results across **all available pages** and exports the data directly to an Excel file using `pandas`. 

Built with simplicity in mind, the codebase is short (~130 lines) and removes unnecessary boilerplate while retaining essential anti-bot evasion techniques.

## Features

- **Dynamic Pagination**: Automatically traverses through all search result pages using the "Next" button.
- **Rich Data Extraction**: Captures product Title, ASIN, Current Price, Original Price, Discount, Rating, Review Count, Sponsored Status, and the Product URL.
- **Anti-Scraping Evasion**: Uses browser-like headers, User-Agent rotation, session cookie warm-ups, and polite random delays between requests to minimize CAPTCHA blocks.
- **Simple Pandas Export**: Drops all parsed data directly into a clean `results.xlsx` file.
- **Flexible URL Input**: Accepts the target Amazon search URL interactively via a prompt or directly via command-line arguments.

## Prerequisites

- Python 3.7+
- Recommended to use a virtual environment.

## Installation

1. Clone or download this project.
2. Install the required dependencies:

```bash
pip install requests beautifulsoup4 pandas
```
*(Note: `pandas` will automatically install `openpyxl` under the hood to handle Excel `.xlsx` files, but you only interface with `pandas` in the code).*

## Usage

You can run the scraper by executing the main script (`main.py`).

### Option 1: Interactive Prompt

Run the script without any arguments. It will prompt you to enter the Amazon Search URL:

```bash
python main.py
```
*(When prompted, paste your search URL, e.g., `https://www.amazon.com/s?k=gaming+headset`)*

### Option 2: Command Line Argument

Pass the Amazon Search URL directly as an argument:

```bash
python main.py "https://www.amazon.com/s?k=gaming+headset"
```

> **Note:** Always enclose the URL in quotes (`" "`) when passing it as a command line argument to prevent your terminal from misinterpreting special characters like `&`.

## Configuration

The script is designed to be as simple as possible. You can tweak its behavior by adjusting a few constants at the very top of `main.py`:

- `OUTPUT_FILE`: Name of the output Excel file (default: `results.xlsx`).
- `DELAY_MIN` & `DELAY_MAX`: The range of random seconds to pause between page requests. 
- `REQUEST_TIMEOUT`: Timeout in seconds for HTTP requests.

## Handling Amazon Bot Detection

Amazon aggressively combats automated scraping. This script implements sensible evasions (header spoofing, cookie tracking, random delays), but if you run it frequently or from a flagged IP address, you may still hit a CAPTCHA or a temporary block.

**Tips to avoid blocks:**
1. **Increase Delays**: Change `DELAY_MIN` and `DELAY_MAX` to higher values (e.g., `5.0` and `12.0`).
2. **Proxies**: If you intend to scrape heavily, you will need to add a `proxies={"http": "...", "https": "..."}` parameter to the `session.get()` calls.
3. **Change IP**: If running locally and you hit a block, try disconnecting/reconnecting your VPN or restarting your router to get a fresh IP address.

## Disclaimer

This tool is provided for educational and research purposes only. Web scraping Amazon may violate their Terms of Service. Use responsibly, be respectful of server load, and consult Amazon's policies before using this software for commercial purposes.
