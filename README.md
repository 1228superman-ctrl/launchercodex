# Codex 动漫启动器 | Codex Anime Launcher

**Unofficial Agent Skill for creating personalized Codex intro videos with synchronized sound, and optionally launching Codex from a separate Windows shortcut.**  
**非官方 Agent Skill：制作 Codex 动漫风格启动视频与渐强配乐，可选独立 Windows 快捷方式启动。**

[简体中文说明 / 中文教程](README.zh-CN.md) · [Install on Windows](docs/windows-setup.md) · [Sound timeline](docs/audio-design.md) · [Release notes](RELEASE_NOTES.md)

> **Beta scope:** This tool edits and combines **user-supplied video footage**. It does **not** generate anime art or video from text, install copyrighted characters/music, patch the Codex application, or reliably set custom picture backgrounds inside the native Codex chat UI. The optional shortcut integration is **Windows-only and requires local testing**.

## What works

- **Edit** existing video clips into a horizontal H.264 MP4; optionally create a vertical blurred-backdrop version with the **same requested frame rate**.
- **Synthesize** keyboard, wheel and click sounds, triggered by events from a JSON timeline.
- **Mix** your own legally usable music: no song while text scrolls or during icon transition; progressive volume during reveal, fade out at UI appearance. Original video audio is discarded to avoid leakage.
- **Verify** stream format, playback decoding, duration, phase loudness and byte-identical video stream after soundtrack replacement.
- **Optionally** create a separate Windows `.lnk` pointing to a helper that plays an MP4 via `mpv` and then opens the **original shortcut**. Backup and restoration scripts are included.

## Requirements

- Python **3.10+** (standard library; no `pip install` required for media scripts)
- FFmpeg (`ffmpeg` and `ffprobe` on `PATH`)
- Your own video clips; your own or appropriately licensed music is optional
- Windows PowerShell 5.1+ and `mpv` **only if** you choose to use the Windows launcher

## Install as an Agent Skill

Copy this **entire folder** to a Skills directory supported by your agent, e.g.:

```text
YOUR_PROJECT/.agents/skills/codex-anime-launcher/SKILL.md
```

In Codex, ask:

> Use the **codex-anime-launcher** Skill to plan a custom anime-style intro for Codex. Inspect my environment first, propose changes, then wait for confirmation before modifying anything.

The agent can use tools available in *your* environment to create original reference art/video separately; **the included scripts only process footage you already have**.

## Quick video + audio workflow

Create `work/` and `exports/`, provide two or more MP4 clips and a soundtrack you may use. Times in `templates/audio_timeline.json` are a **12-second example only**; calibrate to actual output duration and scene events.

```bash
python scripts/check_environment.py
python scripts/build_animation.py --clips input/scene1.mp4 input/scene2.mp4 --output work/silent.mp4 --portrait-output work/portrait_silent.mp4 --fps 30
python scripts/generate_sound_effects.py --timeline templates/audio_timeline.json --output work/foley.wav
python scripts/sync_music.py --video work/silent.mp4 --foley work/foley.wav --music input/MY_LICENSED_MUSIC.mp3 --timeline templates/audio_timeline.json --output exports/with_music.mp4
python scripts/verify_output.py --video exports/with_music.mp4 --compare-video-to work/silent.mp4 --timeline templates/audio_timeline.json
```

If you have **no music**, omit `--music`; use an output filename that does not already exist. The pipeline never overwrites the supplied footage. Edit the timeline to match the **real duration** before generating sound; scene source duration determines final duration. For a reproducible minimal technical test requiring no personal media:

```bash
python -m unittest discover -s tests -v
```

For the Windows shortcut, read [the platform-specific steps](docs/windows-setup.md); they are **not** performed by installing the Skill. Default behavior is to create a **separate** shortcut, preserving Codex as installed.

## Gojo V13, text-only example

[Gojo V13 workflow](examples/gojo_v13_workflow.md) explains the timing decisions derived from one iteration of a real production: typing until 2.39s, no music through the scrolling and icon sequence, music starts at 10.625s and rises through reveal, then fades from 19.375s. The copyrighted song and visuals are **not included**.

## Limitations, privacy and rights

- The media pipeline is cross-platform. **Shortcut helpers are Windows-only** and their `mpv`/Codex behavior varies by machine; beta testers should verify launch/fallback/restore locally.
- Editing a **Windows shortcut icon** is not changing the bundled Codex application icon or taskbar icon. A video showing a themed UI is not proof of native application wallpaper support.
- Record or supply sanitized footage. **Do not publish chats, API credentials, business records, or other private material** in demonstrations.
- Code is MIT-licensed. Third-party music, anime characters, assets, fonts and product trademarks remain under their owners' rights. Users must obtain permissions for public use.
- This community project is **not affiliated with or endorsed by OpenAI**.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [CHANGELOG.md](CHANGELOG.md). Bug reports with OS, media metadata (not private footage), FFmpeg version, and reproduction steps are welcome.
