# GitHub Profile Upgrade Pack — November 2026

## Files included
- `README.md` — updated profile README with dynamic sections and portfolio link.
- `.github/workflows/contribution-snake.yml` — daily animated contribution snake, published to the `output` branch.
- `.github/workflows/github-metrics.yml` — daily advanced metrics SVG.
- `.github/workflows/update-profile-content.yml` — daily refresh of repository showcase and recent public activity.
- `.github/scripts/update_profile.py` — script that fetches your public repositories and public events from GitHub.
- `index.html` — standalone personal portfolio landing page.

## Install
1. Open your profile repository: https://github.com/aruncx/aruncx
2. Upload/replace the files and folders from this pack, preserving the folder structure.
3. In **Settings → Actions → General**, allow GitHub Actions and read/write permissions for workflows.
4. In **Settings → Pages**, choose **Deploy from a branch**, select `main` and `/ (root)`, then save.
5. Your portfolio URL will be: https://aruncx.github.io/aruncx/
6. Open **Actions** and manually run each workflow once:
   - Generate contribution snake
   - Update GitHub metrics
   - Refresh profile content

## Notes
- The contribution snake is published to the `output` branch; do not delete that branch after the first successful run.
- The project showcase lists your public, non-forked, non-archived repositories and sorts them by stars. It refreshes daily.
- Recent activity uses GitHub's public events API. It cannot display private activity and GitHub may return only a limited recent event window.
- The metrics workflow writes `github-metrics.svg` to the repository root.
- If your repository's default branch is not `main`, update the workflow references/Pages branch accordingly.
- If GitHub Actions fails to push, check **Settings → Actions → General → Workflow permissions → Read and write permissions**.
- External SVG/stat services can occasionally be rate-limited or temporarily unavailable; the locally generated metrics SVG reduces dependence on third-party README-stat hosts.
