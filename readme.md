# Random Velechins Bot

Telegram bot that generates and sends plots of the distribution of the sum of independent discrete random variables with given probabilities.

Features
- Accepts an array of probabilities (floats) whose sum must be 1.
- Supports up to 20 probabilities.
- Generates PNG plots showing the distribution of sums for a single k or a range of k.

Requirements
- Python 3.8+
- See `requirements.txt` for exact dependencies (aiogram, numpy, matplotlib, etc.)

Quick start

1. Clone repository and create venv (recommended)
   ```sh
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Configure bot token
   - Set environment variable BOT_TOKEN or edit `config.py` (do not commit secrets).
   - Example `.env` (if used):
     ```
     BOT_TOKEN=your_token_here
     ```

3. Run the bot
   ```sh
   python bot/main.py
   ```

Usage (Telegram)
- /start — begin input sequence.
  1. Send an array of probabilities separated by spaces, e.g.:
     ```
     0.2 0.3 0.5
     ```
     (Sum must be 1, up to 20 numbers.)
  2. Send k or a range:
     - Single k: `2`
     - Range: `1 3`
- The bot replies with a PNG plot of the distribution and a short caption.


