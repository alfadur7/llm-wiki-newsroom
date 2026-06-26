"""`tools/_ingest/suggest_links.py` — English compound-alias detection.

Regression for the post-port gap: a PascalCase stem (`OpenSourceAI`) is matched
verbatim by Pass 1's `\\bOpenSourceAI\\b`, which English prose written spaced
("Open Source AI") never satisfies. The spaced title is registered as an alias
so the unlinked mention is detected.
"""
from _ingest import suggest_links as sl


def test_english_alias_from_multiword_title():
    assert sl._title_english_aliases("Open Source AI", "OpenSourceAI") == ["Open Source AI"]
    assert sl._title_english_aliases("Open Source Initiative", "OpenSourceInitiative") == ["Open Source Initiative"]
    # Subtitle / parenthetical stripped to the lead phrase.
    assert sl._title_english_aliases("Model Licensing — terms & scope", "ModelLicensing") == ["Model Licensing"]


def test_english_alias_skips_non_targets():
    assert sl._title_english_aliases("Mozilla", "Mozilla") == []          # single word → stem pass
    assert sl._title_english_aliases("앤스로픽", "Anthropic") == []        # Korean → korean path
    assert sl._title_english_aliases("코어 뱅킹", "CoreBanking") == []     # Hangul phrase → korean path


def test_find_unlinked_detects_spaced_mention_via_alias():
    body = "The debate centers on Open Source AI and the Open Source Initiative."
    stems = {"OpenSourceAI", "OpenSourceInitiative"}
    alias_map = {"Open Source AI": "OpenSourceAI", "Open Source Initiative": "OpenSourceInitiative"}
    hits = {h["stem"]: h for h in sl.find_unlinked(body, stems, alias_map=alias_map)}
    assert hits["OpenSourceAI"]["count"] == 1
    assert hits["OpenSourceAI"]["alias"] == "Open Source AI"
    assert hits["OpenSourceInitiative"]["count"] == 1


def test_pascalcase_stem_alone_misses_spaced_prose():
    # Without the alias, the stem pass (`\bOpenSourceAI\b`) cannot match the
    # spaced prose form — this is exactly the gap the alias closes.
    body = "A discussion of Open Source AI."
    assert sl.find_unlinked(body, {"OpenSourceAI"}, alias_map=None) == []
    hits = sl.find_unlinked(body, {"OpenSourceAI"}, alias_map={"Open Source AI": "OpenSourceAI"})
    assert hits and hits[0]["stem"] == "OpenSourceAI"


def test_alias_match_is_case_insensitive_and_word_bounded():
    alias_map = {"Open Weights": "OpenWeights"}
    # case-insensitive
    assert sl.find_unlinked("running open weights models", {"OpenWeights"}, alias_map=alias_map)
    # word-bounded — no match inside a larger token
    assert sl.find_unlinked("OpenWeightsRegistry", {"OpenWeights"}, alias_map=alias_map) == []


def test_already_linked_spaced_form_not_flagged():
    body = "See [[OpenSourceAI|Open Source AI]] for the definition."
    out = sl.find_unlinked(body, {"OpenSourceAI"}, alias_map={"Open Source AI": "OpenSourceAI"})
    assert out == []
