name: Refresh GitHub Profile Content

on:
  schedule:
    # Automatically update every day at 00:00 UTC
    - cron: "0 0 * * *"

  workflow_dispatch:

  push:
    branches:
      - main
    paths:
      - '.github/scripts/update_profile.py'
      - '.github/workflows/update-profile-content.yml'

permissions:
  contents: write

jobs:
  refresh:
    name: Update Projects and Recent Activity
    runs-on: ubuntu-latest

    steps:

      # 1. Checkout repository
      - name: Check out profile repository
        uses: actions/checkout@v4

      # 2. Configure Python
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      # 3. Install required dependencies
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install requests

      # 4. Refresh GitHub projects and activity
      - name: Refresh project showcase and recent activity
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_USERNAME: aruncx
        run: |
          python .github/scripts/update_profile.py

      # 5. Commit updated README
      - name: Commit updated profile sections
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

          git add README.md

          if ! git diff --cached --quiet; then
            git commit -m "Update GitHub profile projects and activity"
            git push
          else
            echo "No README changes detected."
          fi
