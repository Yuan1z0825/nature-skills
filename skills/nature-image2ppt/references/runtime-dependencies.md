# Runtime Dependencies

Image2PPT runs entirely from this Skill directory. It neither imports another Skill
nor requires another command-line package.

## Python

Use Python 3.10 or later and install the bundled requirements:

```bash
python -m pip install -r <image2ppt-root>/requirements.txt
```

Copying or synchronizing the Skill does not install Python packages. Run the
command above in the Python environment that will execute the CLI, then require a
successful `doctor --json` result before preparing an input. Prefer a dedicated
environment over modifying the operating system Python.

Required packages are pypdfium2, Pillow, NumPy, Requests, PyYAML, and OpenAI. The
OpenAI package supports the optional image-generation fallback; OCR uses Requests.
The builder writes OOXML directly and does not require `python-pptx`.

Run without installation:

```bash
python <image2ppt-root>/cli/image2ppt/cli.py --help
```

Optionally install the bundled wrapper:

```bash
python -m pip install --editable <image2ppt-root>/cli
image2ppt --help
```

## System programs

- Windows: PowerPoint automation plus PowerShell is preferred for rendered QA.
- Linux/macOS: LibreOffice/`soffice` is required for Office input conversion and
  rendered QA.
- Fonts: install a usable sans font; Noto Sans CJK or Microsoft YaHei is strongly
  recommended for Chinese pages.
- ImageMagick is optional for formula PNG conversion and unusual image formats;
  Pillow is the primary image processor.
- Formula rendering optionally uses a TeX engine plus `dvisvgm`, `pdf2svg`, or
  ImageMagick. Missing formula tooling is a hard failure for formula-bearing pages
  unless the user explicitly approves omission of that exact formula.

Ubuntu/Debian example:

```bash
sudo apt-get install libreoffice-impress fonts-noto-cjk imagemagick
```

## Configuration

Persistent secrets live in the active `config.yaml`: the directory selected by
`IMAGE2PPT_CONFIG_HOME`, then the project-level Skill root, then the legacy
`~/.image2ppt/` location. Process environment variables take precedence. Do not
place a real token/key in a run directory, Prompt, manifest, report, or source control.

Run the independent checks:

```bash
python <image2ppt-root>/cli/image2ppt/cli.py doctor --json
```

Doctor is the sole runtime preflight. It reports Python imports, local
CLI/resources, LibreOffice/PowerPoint rendering, OCR endpoint/model/token/fallback,
image backend readiness, fonts, Pillow, and ImageMagick. It never makes an OCR
request unless a separate smoke test explicitly does so.
