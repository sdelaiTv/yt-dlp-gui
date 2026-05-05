# yt-dlp Desktop GUI Mockup

This is the first visual draft before implementation.

```
+----------------------------------------------------------------------------------+
| yt-dlp Desktop                                           Theme: Dark    v0.1     |
+----------------------------------------------------------------------------------+
| URL / Playlist                                                                  |
| [ https://www.youtube.com/watch?v=...                                       ]   |
| [ + Add URL ] [ Clear ]                                                          |
|----------------------------------------------------------------------------------|
| Save To                                                                          |
| [ C:\Downloads\yt-dlp                                                      ] [..]|
|----------------------------------------------------------------------------------|
| Download Mode       Format                  Audio Format         Quality          |
| ( ) Video + Audio   [ bestvideo+bestaudio] [ mp3           ]   [ best      ]    |
| ( ) Audio only      [ best               ] [ m4a           ]                     |
|----------------------------------------------------------------------------------|
| [x] Download playlist      [ ] Embed metadata      [ ] Write thumbnail           |
| [ ] Write subtitles        [ ] Write auto-subs     [ ] Restrict filenames        |
| Subtitle languages: [ en,ru ]   Subtitle format: [ srt ]                         |
|----------------------------------------------------------------------------------|
| Advanced                                                                         |
| Proxy: [ http://127.0.0.1:8080 ]     Cookies from browser: [ firefox        ]   |
| Cookies file: [ C:\cookies.txt                                            ] [..]|
| Extra args:   [ --concurrent-fragments 4 --limit-rate 4M                     ]   |
|----------------------------------------------------------------------------------|
| Command Preview                                                                   |
| yt-dlp --paths "C:\Downloads\yt-dlp" --format "bestvideo+bestaudio" ... URL      |
|----------------------------------------------------------------------------------|
| Status: Ready                                                                     |
| Progress: [###########------------------------------] 28%                         |
|                                                                                   |
| [ Start Download ] [ Stop ] [ Check URL ] [ Open Folder ] [ Copy Command ]       |
|----------------------------------------------------------------------------------|
| Log                                                                               |
| [18:45:01] Resolving URL...                                                       |
| [18:45:02] Downloading webpage                                                     |
| [download]  28.5% of 93.52MiB at 4.11MiB/s ETA 00:16                             |
| ...                                                                               |
+----------------------------------------------------------------------------------+
```

Implementation note:
- The app maps UI options directly to `yt-dlp` CLI flags.
- Final command is visible before launch for transparency/debugging.
