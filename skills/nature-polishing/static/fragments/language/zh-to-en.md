# Language: Chinese-to-English

When the source is Chinese or strongly Chinese-influenced English, do not translate clause-by-clause.

## Workflow

1. Extract the core propositions first. List them in plain English before drafting prose.
2. Reconstruct explicit logical links: contrast, cause, implication, limitation. Chinese academic prose often elides these connectives — restore them.
3. Verify terminology, causality, and hedging strength against the source.
4. Keep technical terms, gene/protein names, model names, dataset names, and statistical terms stable; do not "translate" them into rough paraphrases.
5. Apply the English sentence and paragraph rules from `language/en.md` only after the logic is rebuilt.

## Common Chinese-influenced patterns to fix

- Topic-comment chains rewritten as subject-verb sentences.
- Strings of short clauses joined by commas — split or add connectives.
- Vague generalizations (`many studies have shown`) — convert to specific citations or remove.
- Hedging asymmetry: Chinese drafts often understate; English Nature-style asks for precise hedging matched to evidence strength, neither over- nor under-claiming.
- Repetition of the topic noun where English would use a pronoun or omit it.
