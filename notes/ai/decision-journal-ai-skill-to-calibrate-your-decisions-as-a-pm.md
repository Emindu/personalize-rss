---
title: "/decision-journal: AI skill to calibrate your decisions as a PM"
source: "https://x.com/nurijanian/status/2075881894189670464"
author:
  - "[[@nurijanian]]"
published: 2026-07-11
created: 2026-11-16
description: "A decision memo documents the team's choice. Team members often keep their estimates, base rates, and exit thresholds in their heads. After ..."
tags:
  - "clippings"
---
![Image](https://pbs.twimg.com/media/HO3Zt1GaAAALTyr?format=jpg&name=large)

A decision memo documents the team's choice. Team members often keep their estimates, base rates, and exit thresholds in their heads. After the result is known, people restate their reasoning to align with it. Those who supported the decision recall feeling more confident than the team recorded, while those who opposed it remember warnings that are not verifiable.

A manager then cannot easily distinguish between good judgment and good fortune. A negative outcome can make well-founded reasoning appear negligent. A positive outcome can make flawed reasoning appear insightful.

AI can be useful in this situation by requiring checks before the outcome influences the narrative. The product manager still provides all estimates and makes the final decision. AI prompts the PM to document and evaluate the reasoning so that others can review it afterward.

## How to challenge the call

A static template can ask for expected outcomes, assumptions, and quit conditions. It can accept "improve onboarding" as an outcome. It can accept probabilities that do not total 100%, an assumption that is not supported, or "revisit if it underperforms" as an exit plan.

The PM must use partial evidence to set probabilities they can defend. They must identify the assumptions that could invalidate the decision and look for relevant base rates. They must also set clear thresholds for changing course.

A PM can perform these checks manually. AI lacks independent judgment and cannot make decisions. AI can run these checks consistently with minimal effort. Repeated prompts help prevent teams from omitting base rates or weakening quit conditions under pressure.

It's unclear if this process improves decision-making. However, it does provide reviewers with a record of pre-outcome reasoning.

The \`decision-journal\` skill asks the PM for estimates and checks whether the team can observe each outcome. It confirms that the probabilities add to 100%. It questions estimates clustered near 50% and searches company context for similar decisions. If it finds no base rate, it marks the assumption as \`gut only\`. It rejects a quit condition until the PM supplies a metric, threshold, and check date.

## The contents of a decision record

A product team must choose between a broad rollout and a pilot for an onboarding redesign. The team already has a causal map, a reversibility rating, current evidence, and rejected options. The skill uses these inputs to create a dated record and leaves missing figures blank.

## Decision

The PM writes one sentence that commits to a choice. It names the owner, timing, and reason the choice addresses the root cause. The record also names each rejected option and why the team rejected it.

## Expected outcomes

The PM replaces vague phrases with measures such as \`\[onboarding outcome metric\]\`, \`\[guardrail metric\]\`, and \`\[support metric\]\`. Each outcome receives a \`\[PM-supplied probability\]%\`, and all probabilities must add to 100%.

## Assumptions and base rates

The record lists the assumptions that could break the call. Each assumption needs a source from company history, a similar launch, or an outside base rate. If no source exists, the skill writes \`gut only\` rather than presenting an estimate as evidence.

## Quit conditions

The PM completes this sentence: if \`\[metric\]\` crosses \`\[PM-supplied threshold\]\` on \`\[PM-selected check date\]\`, the team will \`\[rollback, pause, or change the decision\]\`. The reversibility rating sets how early and strict the triggers need to be.

## Results and review

The skill leaves the results blank. It sets \`\[PM-selected review date\]\` for when the team can observe the expected outcomes. The team fills in the results later and compares them with the estimates and assumptions recorded before the decision.

The record preserves the choice and the team's expectations. It also preserves the evidence available at the time, the rejected options, and the new evidence that would change the plan.

## The future reviewer needs the original reasoning

A manager or successor can compare the evidence with the estimates, identify the assumption that failed, and check whether the team followed the quit condition it had set.

This comparison keeps the review focused on the process that produced the call. The team can also defend a course change because it chose the trigger before sunk costs grew.

The final record has an owner, rejected options, PM-supplied estimates, sourced or gut-only assumptions, quit conditions, and a review date. The team can refer to it while the decision runs. After the results arrive, the manager can use it as a fair benchmark.

For your next consequential product decision, create the record before you commit. Write the observable outcomes, supply the probabilities, flag the decision-breaking assumptions, and set the metric, threshold, and date that would make you change course. If you want an AI facilitator to enforce those checks against your company context each time, you need more than a blank decision template.

## Where this skill lives

![Image](https://pbs.twimg.com/media/HM8CNKbawAA-83d?format=png&name=large)

\`decision-journal\` is one of the 200+ skills inside PM OS, the Product Manager's AI Operating System. It runs in Claude Code, Cowork or Cursor on top of your company context files, so the decision records and quit conditions come back grounded in your product, your users, and your real constraints, instead of generic PM advice that could have come from any blog post.

You don't have to assemble any of it. PM OS wires \`decision-journal\` into the broader operating layer alongside workflows for strategy, research, decisions, stakeholder work, and measurement.

## If you want the full system, it's here.