# The System Underneath

You just watched me break down the system that sits behind every engagement I run. The training funnel, the adoption numbers, the flywheel, how I apply 60/30/10 to my own business.

This companion isn't a recap. It's a set of exercises you do with Claude that map all of this onto your actual work. Not hypothetical. Your real processes, your real bottlenecks. Same approach I use when I walk into a Fortune 500.

## Exercise 1: Your 60/30/10 Audit
This is the most important one. In the video I mapped the underwriter's workflow and my own business. Now you do yours.

Copy this into Claude. Replace the bracketed parts with your actual context.

```
    I want to audit my current workflow using the 60/30/10 framework.
    
    Here's my role: [your role, e.g. "operations manager at a logistics company" or "freelance content creator" or "data analyst at a healthcare org"]
    
    Here's a process I do repeatedly that takes too much time: [describe one specific workflow end to end, e.g. "I receive client briefs via email, pull data from three dashboards, build a summary report in Google Docs, get it approved by two people, then send it to the client"]
    
    Break this workflow into the three layers:
    
    60% (Infrastructure): What parts of this are traditional systems, databases, file storage, routing, approval chains, things that already exist and shouldn't be replaced?
    
    30% (Orchestration): What parts are about connecting things, deciding where data goes, structuring how outputs get formatted or routed, the logic layer that makes the raw tools actually useful for my specific context?
    
    10% (AI): What parts could a model handle well? Summarization, extraction, generation, comparison against a standard?
    
    For each layer, tell me:
    - What already exists that I should keep
    - What's missing or broken
    - What I'm currently doing manually that belongs in a different layer
    
    Be specific to my workflow. Don't give me generic advice.
```

What you'll get back: A structured breakdown of your own work that shows you where you're spending time in the wrong layer. Most people discover they're manually doing orchestration work (the 30%) that could be templated or rule-based.

What to do with it: Read it and push back. Tell Claude where it got your workflow wrong. The conversation that follows is where the real insight happens. Claude doesn't know your process. You do. The framework just gives you a lens.
---
## Exercise 2: Find Your Training Data
In the video I talked about how every training engagement generates structured data about where AI fits, where code fits, where humans stay. That data comes out naturally because people are working with their own processes.

You can run a version of this on yourself.
```
    I'm going to describe three frustrations or bottlenecks in my work. For each one, I want you to figure out whether the problem is:
    
    A) Missing infrastructure (the 60% — there's no system, no database, no pipeline for this)
    
    B) Missing orchestration (the 30% — the pieces exist but nothing connects them, routes them, or structures the output)
    
    C) Missing AI capability (the 10% — I need summarization, generation, or extraction that doesn't exist yet)
    
    Here are my three bottlenecks:
    
    1. [describe a task that takes too long]
    
    2. [describe something where you lose information between steps]
    
    3. [describe something where you're doing repetitive mental work]
    
    For each one, diagnose which layer the problem actually lives in, then suggest one concrete thing I could build or change. Not a tool recommendation. A structural change.
```

What this does: It mirrors the "surfacing" stage of the training funnel. When you describe your bottlenecks in specific terms, the diagnosis reveals patterns. Most people think they need AI when they actually need better routing. Some people think they need a new tool when they actually need to restructure a folder.
---
## Exercise 3: The Leverage Map
I showed the "1 person + system = 4 to 6 people" stat. That's not aspirational. It's measurable. You can estimate your own leverage.

```
    I want to calculate my potential leverage from applying the 60/30/10 framework.
    
    Here's what I currently spend my time on in a typical week:
    
    [List 5-7 tasks with rough time estimates, e.g.]
    
    - Reading and summarizing client documents: 6 hours
    - Formatting reports: 4 hours
    - Sending updates to stakeholders: 3 hours
    - Researching competitors: 5 hours
    - Building presentations: 8 hours
    - Email triage and routing: 4 hours
    
    For each task, estimate:
    1. How much of it is infrastructure (already systematized or could be)
    
    2. How much is orchestration (routing, formatting, decision logic)
    
    3. How much is AI-appropriate (generation, summarization, extraction)
    
    Then estimate the time savings if the 60% was properly built, the 30% was designed and templated, and the 10% was handled by AI. Give me a realistic best case with the framework applied and a conservative estimate.
    
    Don't oversell it. I want honest numbers.
```

The "don't oversell it" instruction matters. You want Claude to be straight with you, not tell you everything will be 10x faster. Some tasks don't compress. Some compress dramatically. The interesting part is seeing which ones.
---
## Exercise 4: Design Your Flywheel
The flywheel in the video was: Training → Build → Case Study → Content → Next Client → Training. Each stage feeds the next. It compounds.

You have a version of this in whatever you do. Most people just haven't mapped it.
```
    Help me map my professional flywheel using this structure:
    What I do: [your work in one sentence]
    Who I serve: [your clients, customers, team, audience]
    
    Walk me through these questions one at a time. Don't answer them all at once. Ask me one, let me respond, then move to the next.
    
    1. What's the core thing I deliver that people pay for or value?
    
    2. What data or insight do I generate as a byproduct of doing that work?
    
    3. How could that byproduct become the input for improving the next delivery?
    
    4. What proof or story comes out of a successful delivery?
    
    5. How does that proof reach the next person who needs what I do?
    
    After we go through all five, map it as a loop and show me where the flywheel is currently broken or leaking.
```

The one-at-a-time instruction is important. If Claude dumps all five answers at once, it's guessing. When it asks you each question and you answer from your actual experience, the flywheel it maps back to you will be real.
---
## Exercise 5: Tools vs Patterns — Test Yourself
This is the quickest exercise but it reveals a lot. In the video I drew the line between training that teaches tools (click this button, use this prompt) and training that teaches patterns (how to think about where AI belongs).

```
    I'm going to list five things I currently know how to do with AI. For each one, tell me whether it's a TOOL skill (specific to a product, will break when the interface changes) or a PATTERN skill (transferable, survives any tool update).
    
    1. [e.g. "I use ChatGPT's custom instructions to set my tone"]
    
    2. [e.g. "I break complex tasks into subtasks before prompting"]
    
    3. [e.g. "I use Copilot's tab completion in VS Code"]
    
    4. [e.g. "I structure my project files so any AI can read the context"]
    
    5. [e.g. "I use the /summarize command in Notion AI"]
    
    For each tool skill, give me the pattern underneath it that I should actually learn. The thing that will still work when the product changes.
```

If most of your list comes back as tool skills, that's not a problem. It's a starting point. The patterns are learnable. That's the whole point.

## How to use these
*Don't do all five in one sitting. Pick the one that feels most relevant to where you are right now.*
- If you're trying to figure out where to start: do Exercise 1 (the audit).
- If you already have a workflow and want to speed it up: do Exercise 3 (leverage map).
- If you're building a business or freelance practice: do Exercise 4 (flywheel).
- If you just want a quick gut check on your AI skills: do Exercise 5 (tools vs patterns).

Exercise 2 is the one that keeps giving. Every time you hit a new bottleneck, run it through the three-layer diagnosis. Eventually you stop needing the prompt because you start seeing infrastructure, orchestration, and AI problems automatically.

That's when the framework is yours. Not because you memorized it, but because you practiced it on your own work until it became how you think.