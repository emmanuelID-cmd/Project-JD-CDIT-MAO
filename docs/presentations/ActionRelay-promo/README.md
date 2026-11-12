# ActionRelay 30-second demo

A 30-second English product video for the README, LinkedIn, and other sharing. It ends with **Try the demo** and the repository link.

| File | What it is |
| --- | --- |
| `ActionRelay-30s-demo.mp4` | Final video: 1920×1080, 30 fps, H.264 High + AAC, standard-range BT.709, fast start, about 7.2 MB. Plays in desktop and mobile browsers. |
| `ActionRelay-30s-demo-poster.jpg` | README thumbnail: the first frame with a play button. |
| `ActionRelay-30s-demo-endcard.jpg` | Final frame with the call to action. |
| `promo.html` | Source animation. Open it in a browser to preview; click to replay. |
| `ui/` | Interface stills cropped from the continuous walkthrough in `../ActionRelay-review/actionrelay-demo.html`, plus the project logo. |
| `record_promo.py` | Renders `promo.html` frame by frame with Playwright and encodes the MP4 with ffmpeg. |

## Content

1. Brand open (also the poster frame).
2. The problem, taken from the Customer Support Specialist job description: SLA pressure, routine volume, and HIPAA-bound handoffs.
3. Six agents passing one version-checked handoff packet.
4. A routine request resolved with the approved form.
5. Agent activity visible to staff.
6. A sensitive request routed to a person.
7. Admin overview and guardrails.
8. End card: **Try the demo** · `github.com/emmanuelID-cmd/Project-JD-CDIT-MAO`.

All tickets, counts, and charts are synthetic. The video makes no claim about CDIT ticket volumes or measured savings. The music is the Open Circuit track already embedded in the walkthrough HTML, looped to 30 seconds.

## Rebuild

Requires Python with `playwright`, an installed Chrome, and an ffmpeg executable.

```powershell
# Extract the walkthrough's music once.
python -c "import re,base64;t=open('../ActionRelay-review/actionrelay-demo.html',encoding='utf-8').read();open('music.wav','wb').write(base64.b64decode(re.search(r'<script id=\"open-circuit-audio\"[^>]*>([^<]+)</script>',t).group(1).strip()))"
python record_promo.py promo.html build --video ActionRelay-30s-demo.mp4 --music music.wav --ffmpeg C:\path\to\ffmpeg.exe
```

`record_promo.py promo.html qa --stills 0,6.5,12.6` renders single frames for review. `build/` and `music.wav` are working files; do not commit them.
