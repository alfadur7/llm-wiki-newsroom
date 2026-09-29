---
layout: default
title: "Scooping the Rice, Leaving the Stones: Can Jev Find the Bad Pages in an LLM Wiki?"
seo_title: "Scooping the Rice, Leaving the Stones: Jev and an LLM Wiki"
permalink: /scooping-stones/
description: >-
  We tried Jev to find the bad pages. What we learned was about the rice.
article_schema: true
schema_inlanguage: en
schema_url: "https://alfadur7.github.io/llm-wiki-newsroom/scooping-stones/"
schema_keywords: "Jev, judge model, LLM as a judge, AI evaluation, preregistration, null result, base rate, AUC, blind labeling, cohort effect, wiki quality, LLM wiki, Karpathy LLM Wiki, knowledge factory, source fidelity, attribution errors, Claude Code, multi-agent"
hreflang_en: "https://alfadur7.github.io/llm-wiki-newsroom/scooping-stones/"
hreflang_ko: "https://alfadur7.github.io/llm-wiki-newsroom/ko/scooping-stones/"
---

*Read this in [한국어]({{ '/ko/scooping-stones/' | relative_url }}).*

A common complaint about AI-maintained wikis is that they're easy to build and hard to keep good. Once there are a few thousand pages, nobody re-reads them all, and the mistakes that matter (a quote pinned on the wrong person, a hedge that quietly disappeared) sit there looking exactly like the pages that are fine.

In September 2026, [TypeSafe AI](https://docs.typesafe.ai) released Jev, a judge model that doesn't generate text at all: you ask it a yes/no question and it returns a probability. The idea seemed obvious. Score every page, re-read the lowest-scoring ones first, and quality maintenance stops being a matter of luck.

We build wikis with [LLM Wiki Newsroom](https://github.com/alfadur7/llm-wiki-newsroom), an open-source framework, and we run it on two of them: a private Korean wiki of about 2,400 pages, and this public English one that anyone can inspect. We tried Jev on both. On the public wiki we tried it twice, with the rules written down before any result existed, and got a null: Jev's ranking found defective pages no better than chance, though with a wide margin of error. What's worth sharing is why, because the reason applies to any screening tool you might bolt onto an AI-written corpus.

The title comes from a Korean kitchen chore called *jorijil*. Rice bought at the market used to come with small stones mixed in, and biting down on one is memorable. So before cooking, you'd put the rice in a bowl of water and swirl it with a *jori*, a small scoop woven from bamboo. The grains are light, so the swirling lifts them into the scoop. The stones are heavy and stay at the bottom of the bowl. Nobody inspects the rice grain by grain; the scoop sorts the whole bowl at once, by weight.

That's the job we wanted Jev to do. A wiki whose pages vary widely in quality is rice with stones in it. The careful way to find the stones is to inspect every grain: have an LLM reviewer read each page against its original and write up what's wrong. In our runs that came to roughly 39,000 tokens per page, counting the instructions the reviewer loads, the page, the original and the report it writes. (That figure comes from our session logs; it's the only public-wiki number here you can't recompute from the repo.) Jev reads the page and the original too, but it only answers up to three yes/no questions and writes nothing back, which came to about 13,000 input tokens per page. If its low scores reliably pick out the bad pages, the expensive reviewer only has to read those.

If you didn't grow up with a jori, think of a medical screening test. Everyone gets a cheap test, and only the people who test positive get the expensive one. That saves work under two conditions. The cheap test has to actually separate the sick from the healthy. And the condition can't be nearly universal, because then you'd end up giving almost everyone the expensive test anyway. When the condition is rare, a third problem appears: you need a very large sample just to find out whether the test works. What follows is which of these our two wikis turned out to be.

## Key takeaways

- **Measure the defect rate before you build the screen.** How much work a screen saves depends first on how common defects are, and only then on how well it ranks. We had to review a sample of pages to find out, and that turned out to be the most useful thing we did.
- **Our two wikis sit at opposite ends.** In the private wiki, 9 of 15 freshly written pages had a serious defect. In the public wiki, 4 of the 62 pages written by the current pipeline did (6.5%).
- **Jev's early signal was a cohort effect.** In the first round Jev looked promising (AUC 0.685). The signal came from four older pages written by an earlier version of the pipeline, three of them defective. Among pages written by the current pipeline, the AUC was 0.491.
- **Small stones everywhere, big ones rare.** Every page in the public wiki had at least one defect, and most had a moderate one. But of the 330 defect reports on the newest 32 pages, only 2 were serious.
- **What we're changing.** The Jev scorer isn't shipping. Instead, every source page in the public wiki will get a full review, starting with the reviews we held back for the experiment.
- **What you can check.** The preregistration, every blind label, the frozen page hashes, Jev's scores and the analysis script are [in the repo](https://github.com/alfadur7/llm-wiki-newsroom/tree/main/docs/experiments/judge-model-2026-09). The private-wiki numbers can't be checked, and we say so wherever they appear.

## The idea, and what came before it

In LLM Wiki Newsroom, a crew of Claude Code agents writes the pages, and a separate reviewer role, called the Desk, reads each page against its original and reports defects. (The architecture is in [The Knowledge Factory]({{ '/knowledge-factory/' | relative_url }}).) The Desk is the expensive part. Every review is a full read of a page and its source, so in the public wiki it only runs automatically on source pages that cross a rule that costs almost nothing to compute: at least seven claims tagged as fact and at least three quotations.

That rule is a crude scoop: it sorts by counting claims and quotes, not by reading. The question was whether Jev could be a better one. For each source page, we gave Jev the page and the original side by side and asked up to three questions (the third only where a claim names someone who has their own page in the wiki):

1. Is each claim's context preserved, or has a hedge, a condition or a scope been dropped?
2. When the original gives both halves of an argument, does the page keep both?
3. Is each named speaker actually the person or organization that said it in the original?

Each answer is a probability, but we didn't treat it as one, because of what we'd already seen on the private wiki.

Before this experiment, we'd measured Jev on the private wiki. There its probabilities couldn't be taken at face value: expected calibration error was around 0.17 to 0.20 on two of the questions, higher scores weren't reliably more accurate, and sending the identical request twice moved the score by 0.013 on average and up to 0.10 (598 repeated pairs), enough to reshuffle pages near any cut-off. So we used the scores only to rank pages. As a ranking, Jev looked strong: on one of the questions its AUC was 0.80, while the existing rule scored 0.37, worse than random.

The same measurement also produced the number that ended the idea of using Jev to choose which new pages to review. **An estimated 44% of pages failed that one question alone** (from a 60-page stratified sample). With nearly half the pages defective, any page a scoop sets aside still has close to even odds of being bad, so you end up reviewing almost everything anyway. So on the private wiki we stopped choosing: every new source page now gets the Desk. A later batch of 15 freshly written pages backed that up, with critical or high defects on 9 of them, and in that same small batch Jev's ranking had nothing to do with how severe the defects were (rank correlation +0.05, n=15).

Jev didn't disappear there, though. The private wiki still has about 2,400 pages published before that rule, and nobody can re-review them all at once. So Jev sets the order in which that backlog gets re-read, and it earns its place in that job: in a checked sample, about 94% of the pages it flagged were defective. But so were about 67% of the pages it didn't flag. It tells you which part of the old sack to go through first; it doesn't tell you the rest is clean.

None of that is verifiable from outside. It's a private wiki, and we're reporting our own measurements of it. That's exactly why we repeated the experiment where anyone can check it.

## Setting it up so we couldn't fool ourselves

The public wiki had only four source pages, so we expanded it to 34. An agent in the framework's Reporter role scouted the sources; the topic is the argument over what "open source" means for AI. Then we did five things we'd have been tempted to skip.

**We held back the review on purpose.** New source pages that cross the rule normally go to the Desk. We turned that off for all 34, so the population would be the pages exactly as the Reporter wrote them. Other pages (people and concept pages) still got their normal review.

**We wrote the rules down first.** [The preregistration](https://github.com/alfadur7/llm-wiki-newsroom/blob/main/docs/experiments/judge-model-2026-09/preregistration.md) was written to a file before any page was labeled or scored. It fixed the primary endpoint: a page is *defective* if it has at least one critical or high defect. It also fixed the comparisons and a decision rule: at least 12 defective pages, and a lower bound on Jev's 95% confidence interval above 0.5, and we'd call the result a signal; otherwise we'd add about 25 sources and measure again. The file lived outside git until it was published alongside this article, so that ordering rests on our word.

**We labeled blind, twice per page.** The labelers were not people. Each was an AI agent running the Desk's review procedure. Two separate agents (labelers A and B) reviewed each page against its original, four pages per call (two in round one's last call), with the same prompt every time, and each got a different grouping of pages. When they disagreed on the endpoint, a third labeler decided. None of them was told about Jev, the experiment, or problems we already knew about, and all were told not to read the project log, the git history or the tools folder, which is where those facts live.

**We kept the questions away from the labelers.** The three Jev questions are written as checks for a page to pass. If they'd been in the files the Desk reads, the labelers would have been primed to look for exactly what Jev was asked about. So they stayed in a separate folder until labeling was done.

**We scored last.** Jev saw nothing until every label was in: 90 requests in the first round, about 490,000 input tokens, one call per page and question. The label files carry no timestamps, so this too is our word; the score file's timestamps show when Jev was called.

AI labelers are consistent and cheap enough to run on every page, but they aren't human ground truth. The private-wiki measurement was labeled the same way. We come back to what that costs under Limits.

## Round one: a promising number with a catch

Every AUC below is oriented so that above 0.5 means the signal points at the defective pages, and ranks count from the most suspicious page.

Of the 34 pages, 6 were defective, which already missed the "at least 12" condition. Jev's AUC was 0.685, but its confidence interval ran down to 0.38. The existing rule scored 0.345 and page length 0.25, so both pointed the wrong way: the short pages were the defective ones.

That made us look at *which* pages were defective. Three of the six were among the original four pages, written months earlier by an older version of the pipeline, and all three were short. Jev had ranked them 1st, 4th and 6th. Among the 30 pages from the expansion, Jev's AUC was 0.43.

This wasn't in the preregistration. It was an after-the-fact look at the data, so we didn't treat it as a finding. We treated it as a hypothesis: maybe Jev was picking up "old and thin" rather than "wrong".

## Round two: testing the hypothesis we'd just formed

The rule said to expand, so we did. Before choosing a single new source, we added [an amendment](https://github.com/alfadur7/llm-wiki-newsroom/blob/main/docs/experiments/judge-model-2026-09/preregistration.md) to the preregistration. The primary analysis would cover only pages written by the current pipeline, with the original four reported separately. We fixed that in writing because round one had suggested it; fixing it after seeing round two would have been choosing the answer. We also added an analysis stratified by page length, so that neither length nor cohort could pass itself off as a defect signal.

New sources were chosen by topic and type only, favoring reporting that quotes several parties, since that's where attribution goes wrong. The Reporter wasn't told why. It moved fast: round one's scoring finished at 17:26 KST on September 27, and the new sources were fetched at 17:35. We wrote the amendment in between, which, like the preregistration, rests on our word. What the timestamps do show is that no new page had been fetched yet, so there was no score for one to consult.

We ingested 32 more sources and wrote and reviewed six new people and concept pages. The new pages were linked only from the new source pages, so the 34 already-labeled pages stayed untouched; we checked them by hash before and after every step. Then we ran the same two-labeler blind review on the 32 new pages, with a third labeler on the two disagreements, and scored them (84 requests, about 377,000 tokens).

| Population | Pages | Defective | Jev AUC | 95% CI | Rule AUC | Length AUC |
|---|---|---|---|---|---|---|
| **Current pipeline (primary)** | 62 | 4 | **0.491** | 0.20–0.79 | 0.547 | 0.358 |
| All pages | 66 | 7 | 0.692 | 0.41–0.92 | 0.392 | 0.215 |
| Original four | 4 | 3 | 1.000 | — | 0.500 | 0.667 |

*The interval's lower bound is the smaller of two methods (Hanley–McNeil and a 2,000-resample bootstrap), as preregistered; the upper bound is Hanley–McNeil. The script prints both. With only four pages, the original-four row is descriptive.*

Stratifying by page length didn't rescue Jev (AUC 0.556 within length tertiles). The four defective current-pipeline pages sat at ranks 14, 16, 41 and 57 out of 62, so a "re-read the ten lowest scores first" queue would have caught none of them. The hypothesis held when 32 new pages were added: the round-one signal came from the old cohort, and it vanishes when that cohort is set aside. To be fair about how much new evidence that is, the new pages contributed only one of the four defective pages; the other three were already in view in round one.

The decision rule said to expand again. We didn't. At a 6.5% defect rate, collecting 12 defective pages takes about 185 pages, so another 25 sources couldn't change the answer.

## Why this wiki has so few big stones

"Only 6.5% defective" sounds like good news about the pipeline, and partly it is. The full label counts show where the defects actually sit:

| | Defect reports (critical / high / medium / low) | Pages with any defect | Pages with medium or worse |
|---|---|---|---|
| Round one's 34 pages | 1 / 21 / 88 / 284 | 34 of 34 | 32 of 34 |
| Round two's 32 pages | 0 / **2** / 66 / 262 | 32 of 32 | 25 of 32 |

*Counts add up the reports of labelers A and B, so a defect both of them found counts twice; the third labeler's reports aren't included.*

Every page has defects, and most have a medium one: a hedge softened, a reporter's narration attributed to the person being quoted, a link in the page's Connections section that nothing in the body supports. What's rare is the kind of defect that makes a reader believe something false. So why does this wiki have so few of those, when the private one has so many? We have three candidate explanations, in order of how much evidence we have, and one caution.

1. **The pipeline improved.** There's direct evidence inside this wiki: three of the four pages written by the older pipeline were defective, against four of the 62 written by the current one. We wrote the current authoring rules on the private wiki, after running into most of its worst defect classes, and later ported them here. Most of the private wiki's pages were written before those rules existed.
2. **Language.** The private wiki's worst defects were things like a Korean hedge ("알려졌다", roughly "it is reported that") becoming a flat statement, a columnist's opinion turning into an institution's announcement, and numbers mistyped in transcription. A Korean page written from an English original goes through translation, and even from a Korean original, hedges like that tend to fall out in summarizing. Here, English originals become English pages. We haven't measured this; it's a hypothesis.
3. **The sources.** The private wiki is mostly technology news built on press releases, with lots of figures, and a wrong figure is a critical defect. This wiki is analysis, opinion and reporting chosen by the Reporter, with few figures, so its defects tend to be about nuance.

The caution: the line between serious and moderate is shaky. Across both rounds, five pages had A and B disagreeing on the endpoint. In all five, both labelers had flagged the same defect and disagreed only on its severity, three times high against medium and twice high against low. An endpoint that flips on one severity call is noisy, so the 6.5% itself is soft.

## What we took from it

A screen is worth its cost only if it separates bad pages from good ones better than picking at random, and how much reviewing it saves depends on how common the bad pages are. When they're very common, whatever the screen sets aside is still likely to be bad, so it saves little. When they're rare, there's little to find, and you need a large labeled sample just to learn whether the screen works; a small experiment like ours is underpowered. We started by asking "can Jev rank our pages?", and it was the wrong first question. The first question is how many stones are in the rice, and you can only answer it by reviewing a sample. In our case that took 137 blind reviews.

We ran the same kind of experiment on two wikis and hit both ends:

- **Private wiki:** stones in almost every handful, so every new grain gets inspected: every new source page gets the Desk. Jev's job shrinks to choosing which part of the old backlog to go through first, where it finds the stoniest handfuls but can't vouch for the rest.
- **Public wiki:** big stones so rare we couldn't even check whether the scoop leaves them behind, and Jev showed no sign that it does. Small stones are in nearly every handful, so every grain gets inspected here too.

So the change we're making is boring. The private wiki already sends every new source page to the Desk, and the public wiki will now do the same for all of its source pages, starting with the reviews the experiment held back. It has no backlog big enough to need a queue. The scorer that calls Jev stays in a local, uncommitted folder.

We don't think this says Jev is a bad model. On the private wiki its ranking was the best signal we'd measured, and it's still in use there for the backlog. It says a ranker is only worth adding where defects are neither everywhere nor nowhere, and you have to measure the defect rate to know where that is.

## Limits

- **Small numbers.** The primary analysis has 4 defective pages, so its confidence interval spans about 0.2 to 0.8. That rules out a strong effect (an AUC above 0.8) but not a weak one in the 0.6 to 0.7 range.
- **Labels from agents.** Every label came from AI labelers following the Desk procedure, with a third resolving disagreements. They agreed on the endpoint for 61 of 66 pages, but agreement between models of one family isn't the same as being right. The pages were also written by a model of the same family, so there may be blind spots the writer and the labelers share, and this design can't rule that out.
- **Blind by instruction.** The facts the labelers weren't supposed to see were in the same repo. They were told not to read them, and nothing enforced it.
- **A fragile endpoint.** Every disagreement was over the severity of a defect both labelers had found. A differently calibrated labeler could move several pages across the line.
- **One call per question.** On the private wiki, identical repeated calls moved scores by 0.013 on average and up to 0.10, enough to reorder pages with close scores. We didn't re-measure it here.
- **Scores can be re-analyzed, not regenerated.** The scorer that called Jev isn't published, so the repo lets you re-run the analysis on our scores but not produce new ones.
- **The private numbers are ours alone.** Everything about the 2,400-page wiki is our own report of a private measurement, labeled by the same kind of agent.
- **Round one's cohort analysis was after the fact.** Round two tested it under a preregistered amendment, but it still started as a look at data we'd already seen.

## Check it yourself

The [experiment folder](https://github.com/alfadur7/llm-wiki-newsroom/tree/main/docs/experiments/judge-model-2026-09) holds:

- the preregistration with its amendment, and the verbatim labeling prompt
- every label from every labeler (round one's batch A2 in the labeler's full wording; the rest as short summaries, with severity exactly as given)
- the page hashes frozen before each round
- Jev's scores (the model version is recorded only as an opaque tag)
- a script that recomputes the public-wiki numbers above

```
python docs/experiments/judge-model-2026-09/analyze.py 1        # round one
python docs/experiments/judge-model-2026-09/analyze.py 2        # round two
python docs/experiments/judge-model-2026-09/analyze.py labels   # severity table, reviews, request counts
```

It makes no network calls and needs no key. It reads only that folder, including a snapshot of each page's rule status and length taken at the freeze, because the pages themselves are about to be repaired. To see the pages exactly as they were labeled, check out the commit that added the folder; their hashes are in the freeze files. If you get a different number, open an issue.
