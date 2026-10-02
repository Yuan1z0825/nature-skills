# Paper-type taxonomy

Canonical 5-type vocabulary used by both `nature-polishing` and `nature-writing` (and any future skill on the `paper_type` axis).

## The five types

| Type | One-line definition | Reader's central question |
|---|---|---|
| **research** | Reports a phenomenon, mechanism, or finding from primary observation or experiment. | What was found and what does it mean? |
| **methods** | Proposes a new method, protocol, or measurement and demonstrates its advantage. | Does it work? Is it better? Is it reproducible? |
| **hypothesis** | Establishes or rules out a causal explanation through targeted evidence. | Is the proposed mechanism the right one? |
| **algorithmic** | Proposes a procedure, model, system, or device and shows it performs reliably and advantageously. | Does it perform under fair comparison? Where does it fail? |
| **review** | Synthesizes the state of a field, organizing the literature by argument, not by paper. | What is known, where is the disagreement, what is open? |

## Detection guidance

- If the user names a paper type, use it.
- If the manuscript reports experiments testing a stated mechanism → **hypothesis**.
- If the manuscript proposes a procedure/model and reports comparisons → **algorithmic**.
- If the manuscript proposes a measurement or protocol and reports validation → **methods**.
- If the manuscript synthesizes prior literature without new primary data → **review**.
- Otherwise → **research** (default).

## Notes on legacy vocab

Some older notes use a longer taxonomy (mechanism / method / resource / device / model / clinical / materials / computational / interdisciplinary). Map onto the five canonical types:

- mechanism, clinical, materials → **research** or **hypothesis** depending on whether a causal claim is central
- method → **methods**
- model, device, computational → **algorithmic**
- resource → usually **methods** (a dataset/benchmark paper) or **research**
- interdisciplinary → use the dominant argument structure, not the field label

## Skill-specific action layers

Each skill's `static/fragments/paper_type/<type>.md` adds the **action layer** for that skill on top of this taxonomy:

- `nature-polishing` adds diagnostic rules (what to look for, what to fix).
- `nature-writing` adds constructive rules (argument chain, drafting order).

The taxonomy here is the **shared vocabulary**; the action is skill-specific.
