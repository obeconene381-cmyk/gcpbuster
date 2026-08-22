name: Run Lab Automation

on:
  workflow_dispatch:
    inputs:
      lab_url:
        description: 'Lab Catalog URL'
        required: true
        type: string
      cookies_b64:
        description: 'Cookies in Base64 format'
        required: true
        type: string
      bot_token:
        description: 'Telegram Bot Token'
        required: true
        type: string
      chat_id:
        description: 'Telegram Chat ID'
        required: true
        type: string
      region_override:
        description: 'Region Override (optional)'
        required: false
        default: ''
        type: string

jobs:
  execute-automation:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install System Dependencies & Xvfb
        run: |
          sudo apt-get update
          sudo apt-get install -y xvfb libgbm-dev

      - name: Install Python Libraries & Playwright
        run: |
          python -m pip install --upgrade pip
          pip install playwright requests
          playwright install chromium --with-deps

      - name: Run Playwright Script with Virtual Display
        env:
          LAB_URL: ${{ github.event.inputs.lab_url }}
          COOKIES_B64: ${{ github.event.inputs.cookies_b64 }}
          BOT_TOKEN: ${{ github.event.inputs.bot_token }}
          CHAT_ID: ${{ github.event.inputs.chat_id }}
          REGION_OVERRIDE: ${{ github.event.inputs.region_override }}
          PAT_TOKEN: ${{ secrets.PAT_TOKEN }}
        run: |
          xvfb-run --auto-servernum --server-args="-screen 0 1920x1080x24" python main.py
