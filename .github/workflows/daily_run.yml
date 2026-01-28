name: Daily Subsidy Portal Update

on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4  # ここを [] なしの形式に修正
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: pip install requests

      - name: Run main.py
        env:
          AIRTABLE_TOKEN: ${{ secrets.AIRTABLE_TOKEN }}
          AIRTABLE_BASE_ID: ${{ secrets.AIRTABLE_BASE_ID }}
          AIRTABLE_TABLE_NAME: ${{ secrets.AIRTABLE_TABLE_NAME }}
        run: python main.py
