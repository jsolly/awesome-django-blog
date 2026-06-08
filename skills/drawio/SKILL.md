---
name: drawio
description: Generate draw.io diagrams as native .drawio XML files, with optional CLI export to PNG/SVG/PDF.
disable-model-invocation: true
effort: max
---

# Draw.io Diagram Skill

Write native `.drawio` files (mxGraphModel XML). Optionally export to PNG, SVG, or PDF via the desktop CLI — exported files embed the diagram XML so they remain editable in draw.io.

## Workflow

1. Generate mxGraphModel XML for the requested diagram
2. Write to `<name>.drawio` in the working directory
3. If the user wants an export format, run the CLI with `--embed-diagram`, then delete the source `.drawio`
4. Open the result with `open <file>`

Check the user's request for a format preference:

- `/drawio create a flowchart` → `flowchart.drawio`
- `/drawio png flowchart for login` → `login-flow.drawio.png`
- `/drawio svg: ER diagram` → `er-diagram.drawio.svg`
- `/drawio pdf architecture overview` → `architecture-overview.drawio.pdf`

If no format is mentioned, write the `.drawio` file and open it.

### Supported export formats

| Format | Embed XML | Notes |
| -------- | ----------- | ------- |
| `png` | Yes (`-e`) | Viewable everywhere, editable in draw.io |
| `svg` | Yes (`-e`) | Scalable, editable in draw.io |
| `pdf` | Yes (`-e`) | Printable, editable in draw.io |
| `jpg` | No | Lossy, no embedded XML support |

## CLI path

```text
/Applications/draw.io.app/Contents/MacOS/draw.io -x -f <format> -e -b 10 -o <output> <input.drawio>
```

If the CLI isn't found, keep the `.drawio` file and tell the user.

## Gotchas

- **Always generate XML directly.** Mermaid and CSV formats require server-side conversion and cannot be saved as native `.drawio` files.
- **Never include XML comments (`<!-- -->`)** — they waste tokens and can cause parse errors.
- **Escape special characters** in attribute values: `&amp;`, `&lt;`, `&gt;`, `&quot;`
- **Use unique `id` values** for every `mxCell`.
- **Every edge needs geometry**: an edge `mxCell` without a child `<mxGeometry relative="1" as="geometry" />` won't render.
- **Use double extensions for exports** (`name.drawio.png`) — signals the file contains embedded diagram XML.

## Troubleshooting

| Problem | Cause | Solution |
| --------- | ------- | ---------- |
| CLI not found | Desktop app not installed | Keep the `.drawio` file; tell the user to install draw.io desktop |
| Export produces empty/corrupt file | Invalid XML (unescaped chars, comments) | Validate XML well-formedness before writing |
| Diagram opens but looks blank | Missing root cells `id="0"` and `id="1"` | Ensure the basic mxGraphModel structure is complete |
| Edges not rendering | Edge mxCell is self-closing (no child mxGeometry) | Every edge must have `<mxGeometry relative="1" as="geometry" />` |

## Minimal XML skeleton

```xml
<mxGraphModel adaptiveColors="auto">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
  </root>
</mxGraphModel>
```

Cell `0` is the root layer; cell `1` is the default parent. All diagram elements use `parent="1"` unless using multiple layers.

## XML reference

@references/xml-reference.md
