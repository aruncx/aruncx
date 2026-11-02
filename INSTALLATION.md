# GitHub metrics fix for @aruncx

## Files
- `README.md` — updated profile README. Replaces broken third-party statistics and activity graph images with a repository-hosted `github-metrics.svg`.
- `.github/workflows/github-metrics.yml` — generates and commits `github-metrics.svg` daily.

## Install
1. Replace the root `README.md` in `aruncx/aruncx` with this package's `README.md`.
2. Create `.github/workflows/github-metrics.yml` and paste the included workflow.
3. In the repository, open Settings → Actions → General → Workflow permissions.
4. Select **Read and write permissions**, then save.
5. Open Actions → Generate GitHub profile metrics → Run workflow.
6. Wait for the workflow to finish. It should commit `github-metrics.svg` to the `main` branch.
7. Refresh your profile README.

The workflow uses the built-in `GITHUB_TOKEN` and requests repository write permission. If GitHub rejects a permission or API request, inspect the exact failed step before changing token scopes. Do not publish a personal access token in README or commit it to the repository.

## Notes
- The generated SVG is stored in your own repository, reducing dependence on public stats-card hosting services.
- The existing contribution streak image is retained because it was displaying in your screenshot.
- Your existing project showcase/activity workflow and contribution-snake workflow are not replaced by this package.
- The workflow uses `lowlighter/metrics@latest`; the Metrics project documents its plugins and output-to-commit feature in its official repository.
