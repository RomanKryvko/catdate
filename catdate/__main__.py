import os
import sys
from catdate.bot import run_bot

if __name__ == '__main__':
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Put bot API token in BOT_TOKEN env var.")
        sys.exit(1)
    run_bot(TOKEN)
