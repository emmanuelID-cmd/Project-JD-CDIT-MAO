"""Render the ActionRelay promo HTML frame by frame and encode a web/mobile-safe MP4.

Usage:
  python record_promo.py promo.html out_dir --stills 1.5,6,12            # QA stills only
  python record_promo.py promo.html out_dir --video out.mp4 --music music.wav --ffmpeg ffmpeg.exe
"""
import argparse
import asyncio
import subprocess
from pathlib import Path

from playwright.async_api import async_playwright

CHROME = Path.home() / "AppData/Local/Google/Chrome/Application/chrome.exe"
W, H, FPS, SECONDS = 1920, 1080, 30, 30.0


async def render(html: Path, out: Path, times: list[float], ext: str) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=str(CHROME), headless=True,
                                          args=["--hide-scrollbars", "--force-color-profile=srgb", "--lang=en-US"])
        page = await browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1, color_scheme="dark")
        await page.goto(html.resolve().as_uri(), wait_until="load")
        await page.evaluate("document.fonts.ready")
        await page.wait_for_function("[...document.images].every(i => i.complete && i.naturalWidth > 0)")
        for i, t in enumerate(times):
            await page.evaluate(f"window.seek({t})")
            path = out / (f"{i:05d}.{ext}" if ext == "jpg" else f"t{t:05.2f}.png")
            if ext == "jpg":
                await page.screenshot(path=str(path), type="jpeg", quality=95)
            else:
                await page.screenshot(path=str(path))
            paths.append(path)
        await browser.close()
    return paths


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("html", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--stills")
    ap.add_argument("--video", type=Path)
    ap.add_argument("--music", type=Path)
    ap.add_argument("--ffmpeg", type=Path)
    ap.add_argument("--volume", type=float, default=0.55)
    ap.add_argument("--encode-only", action="store_true")
    a = ap.parse_args()
    if a.stills:
        for path in asyncio.run(render(a.html, a.out, [float(x) for x in a.stills.split(",")], "png")):
            print(path)
        return
    frames = a.out / "frames"
    if not a.encode_only:
        for old in frames.glob("*.jpg"):
            old.unlink()
        n = int(SECONDS * FPS)
        asyncio.run(render(a.html, frames, [k / FPS for k in range(n)], "jpg"))
    cmd = [str(a.ffmpeg), "-hide_banner", "-loglevel", "error", "-y",
           "-framerate", str(FPS), "-i", str(frames / "%05d.jpg")]
    if a.music:
        # The 24 s track loops seamlessly; loop once, trim to 30 s, fade in and out.
        cmd += ["-stream_loop", "1", "-i", str(a.music),
                "-af", f"volume={a.volume},afade=t=in:st=0:d=0.4,afade=t=out:st={SECONDS - 1.8}:d=1.8",
                "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2"]
    cmd += ["-t", str(SECONDS),
            "-vf", "scale=in_range=full:out_range=limited:out_color_matrix=bt709,format=yuv420p",
            "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
            "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-maxrate", "2400k", "-bufsize", "4800k",
            "-profile:v", "high", "-level", "4.1", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-movflags", "+faststart", str(a.video)]
    subprocess.run(cmd, check=True)
    print("wrote", a.video, a.video.stat().st_size, "bytes")


main()
