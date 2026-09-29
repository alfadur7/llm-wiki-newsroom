---
title: "Anthropic Details Distillation Campaigns from Alibaba, Moonshot AI, and DeepSeek"
type: source
tags: [distillation, ai-safety, China, ai-policy, national-security]
published: 2026-09-10
scraped: 2026-09-27
source_file: "raw/NewsScrap/Anthropic details distillation campaigns from Alibaba, Moonshot AI, and DeepSeek.md"
source_url: "https://techcrunch.com/2026/09/10/anthropic-details-distillation-campaigns-from-alibaba-moonshot-ai-and-deepseek/"
last_updated: 2026-09-27
---

## Summary

A TechCrunch article by Russell Brandom reports on a report [[Anthropic]] released on 2026-09-10 alleging persistent [[Distillation|distillation]] attacks on its Claude models by China-based AI companies. According to the report, Anthropic observed nearly 200 million exchanges tied to five campaigns that tried to extract Claude's chain of thought, the reasoning traces it normally shows users only in summarized form. The largest campaign, which Anthropic attributes to Alibaba, ran 151 million exchanges between May and July 2026 to produce training material for its Qwen models. A second, attributed to [[MoonshotAI|Moonshot AI]], appeared to route requests directly from the Chinese military. The article carries only Anthropic's account; the accused companies' responses and any external assessment are outside the raw's scope, and although the headline names [[DeepSeek]], the raw body details only the Alibaba and Moonshot campaigns.

## Key Claims

- [fact] [[Anthropic]] — released a report on 2026-09-10 alleging persistent distillation attacks by China-based AI companies that escalated in recent months
- [fact] [[Anthropic]] — states that unauthorized labs developed increasingly sophisticated methods to circumvent its defenses and harvest the capabilities of US frontier models [[anthropic-distillation-campaigns-alibaba-moonshot#Key Quotes]]
- [fact] [[Anthropic]] — states that the campaigns targeted Claude's agentic and tool-use, coding and data-analysis, and logical-reasoning capabilities [[anthropic-distillation-campaigns-alibaba-moonshot#Key Quotes]]
- [fact] [[Anthropic]] — observed nearly 200 million exchanges linked to distillation attacks, which it attributes to five separate campaigns
- [fact] TechCrunch — reports that Anthropic had spoken out about distillation attacks in February and named specific labs at that time
- [fact] TechCrunch — reports that [[OpenAI]] has reported similar distillation activity, which it attributed to [[DeepSeek]]
- [analysis] TechCrunch — assesses the campaigns in Anthropic's new report as larger and more aggressive than those it disclosed earlier
- [analysis] TechCrunch — explains that distillation attacks extract a model's chain of thought so it can be used to train a smaller model on general reasoning through supervised [[FineTuning|fine-tuning]]
- [fact] TechCrunch — reports that Anthropic does not usually expose Claude's internal chain of thought and instead shows "summarized thinking" blocks
- [fact] [[Anthropic]] — reports that the campaigns found techniques that tricked the model into revealing its thinking traces directly
- [fact] [[Anthropic]] — reports that one attacker framed its query as a translation request asking the model to translate its previous working memory into katakana-only Japanese
- [fact] [[Anthropic]] — attributes the bulk of the distillation attempts to a campaign it links to Alibaba, which it calls the largest wholesale distillation effort it has ever observed
- [fact] [[Anthropic]] — observed 151 million exchanges attributed to the Alibaba campaign between May and July 2026, peaking at nearly three million exchanges per day
- [fact] [[Anthropic]] — reports that the Alibaba-attributed exchanges were spread across 3,500 accounts
- [analysis] [[Anthropic]] — attributes those 3,500 accounts to a single effort to produce training material for Alibaba's Qwen models because they shared one fixed chain-of-thought extraction prompt
- [analysis] [[Anthropic]] — reports that a campaign from Moonshot AI, the maker of Kimi, seemed to route requests directly from the Chinese military
- [fact] [[Anthropic]] — reports that one request in the Moonshot campaign asked Claude to assess closed-circuit surveillance footage to determine whether the subject was "behaving abnormally"
- [fact] [[Anthropic]] — reports that nearly 300,000 requests reached Claude over one 10-day period through a network of 5,000 accounts, mainly targeting its Opus model

## Key Quotes

> "Over the last several months, unauthorized labs have developed increasingly sophisticated methods to circumvent our defenses and harvest the capabilities of US frontier models." — [[Anthropic]], distillation report

> "The campaigns we identified targeted some of Claude's most valuable capabilities, including agentic capabilities and tool use, coding and data analysis, and logical reasoning." — [[Anthropic]], distillation report

## Connections

- cites: [[Anthropic]] — the report's figures on five campaigns, 200 million exchanges, and the Alibaba and Moonshot AI attributions are Anthropic's
- references: [[Distillation]] — describes chain-of-thought extraction for supervised fine-tuning of smaller models as an unauthorized attack on a closed model
- references: [[DeepSeek]] — named in the headline and as the lab OpenAI attributed similar distillation activity to
- references: [[MoonshotAI]] — the Kimi maker to which Anthropic attributes a distillation campaign that seemed to route requests from the Chinese military
- references: [[OpenAI]] — reported similar distillation activity and attributed it to DeepSeek
- references: [[FineTuning]] — extracted reasoning traces are used to train smaller models through supervised fine-tuning
- references: [[AISafety]] — the Moonshot campaign's surveillance-footage request is presented as a military use of Claude obtained around Anthropic's defenses
- references: [[anthropic-position-open-weights-models|Anthropic's position on open-weights models]] — gives figures for the industrial-scale distillation Dario Amodei urged a crackdown on in July 2026
