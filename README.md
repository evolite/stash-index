# stash-index

Independent GitHub copy of my Stash plugin index, so the index survives even if the Codeberg one goes away.

- **GitHub index:** https://evolite.github.io/stash-index/index.yml, rebuilt every 15 minutes (and on pushes to `plugins.yml`/`build_index.py`) from each plugin's latest **GitHub release**. See `build_index.py`.
- **Codeberg index:** https://surging9143.codeberg.page/index.yml, updated by each plugin's release workflow. Not touched by this repo.

Names and descriptions are kept in `index.yml`; version, date, download URL and sha256 come from the release.
Plugins that haven't been released from GitHub yet keep their existing entry. To add a plugin, add its entry to `index.yml`
(id, name, description, any version/path) and a line to `plugins.yml`.
