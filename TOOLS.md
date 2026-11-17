# Tools (pinned)

| Tool | Version | Notes |
|---|---|---|
| SolidCraft (`solidcraft-cli`, GUI) | 0.41.0 | User Flatpak `io.tangencylabs.solidcraft`; `~/.local/bin/solidcraft-cli` runs its native binary (`~/.local/share/flatpak/app/io.tangencylabs.solidcraft/current/active/files/bin/solidcraft-cli`). Design format 55: files saved by it do not open in 0.30.1. Files still at format 48 (built by 0.30.1) open fine; they move to 55 when their product is rebuilt. Upgraded 2026-11-17 (user decision: the 0.30.1 AppImage was gone). No nightly/RC builds for committed files. Commit a version bump as its own commit. |
| git + git-lfs | git 2.43 | LFS patterns in `.gitattributes`. |
| Python | 3 (system) | only for generator scripts under `<product>/tools/` |
