# The Prompt Library

This is a living document. Every prompt in here came from a real conversation with a real member working on a real business. None of them were written in the abstract. They were built during live VIP and Afternoon Tea sessions where someone brought a problem, we worked through it as a group, and the framework that came out of that conversation got turned into a prompt you can paste into Claude.

That matters because most AI prompt collections are generic. "Write me a marketing plan." "Summarize this document." Those work fine for general tasks but they do not know your industry, your constraints, or your specific situation. These prompts are different. Each one encodes a specific strategic framework. When you fill in your details and run it, Claude is not just answering a question. It is applying a tested way of thinking about a business problem to your particular case.

I am updating this library after every session. As the community grows and more industries show up in the calls, the prompt coverage will expand. If you run one and it does not land right for your situation, post about it in the community. That feedback shapes the next round.

## How These Are Organized

Each section below corresponds to a session. Inside each session you will find the prompts labeled by what they solve. Grab the one that fits your current problem, paste it into Claude, fill in your details, and run it.

**Tips for getting the most out of them:**

Be specific when you fill in the blanks. "I run a business" gives Claude nothing to work with. "I run a luxury residential cleaning company in Portland with 12 independent contractors" gives it everything.

Paste in extra context if you have it. Your current expenses, your client list, notes from a strategy call, a competitor's pricing page. The more Claude knows about your situation, the sharper the output.

Push back on the first response. If Claude gives you something generic, tell it. Say "that is too broad, here is more detail" and add context. First response is a starting point.

Run multiple prompts in sequence. Start with Prompt 7 (problem mapping), then run Prompt 2 (minimum viable fix), then Prompt 3 (manual to product). They build on each other.

## Session 1 — VIP Drawing Room (April 2026)

Frameworks covered: Profit First for AI, the Gum Wrapper Principle, Workflow First / Software Later, Anchor Pricing, Revenue Share vs. Cash Upfront, the Free Value Funnel, Never Start with AI.

Members who shaped these: Ruby (luxury cleaning, Portland), Barkley (PE / high net worth), Eric (multi-business scaling), Latum (security pipeline), Alex (Grammy-winning producer), Megan (event staffing, SEO).

**Prompt 1: Zero-Spend Audit** *What it solves: Figuring out what you can accomplish right now without buying anything new.*
```
    I run [YOUR BUSINESS]. I currently spend [AMOUNT] per month on tools, software, and subscriptions. Using a Profit First framework where Sales minus Profit equals Expenses, identify: (1) What outcomes can I get right now with zero new spending? (2) Where am I spending money before I have traction? (3) What is the simplest proof of concept I could offer a client this week using only Claude and my existing knowledge?
```

**Prompt 2: Minimum Viable Fix** *What it solves: Finding the cheap version of an expensive solution so you can prove it works before investing.*
```
    I work in [YOUR INDUSTRY] and the expensive solution to [YOUR PROBLEM] costs [AMOUNT]. Help me design a minimum viable fix that: (1) Costs under $100/month, (2) Creates a measurable outcome within 2 weeks, (3) Generates data I can use to justify or design the expensive solution later.
```

**Prompt 3: Manual Process to Product What it solves:** *Turning something you do well by hand into something you can package and sell.*
```
    Here is my current business and what I do manually: [DESCRIBE YOUR WORKFLOW]. (1) What parts of my manual process could I package and sell as a low-cost service right now? (2) Where will that process break at scale? (3) What would the software version look like, built from those specific breaking points?
```

**Prompt 4: Agency Undercut Strategy What it solves:** *Competing with established service providers by using AI internally to deliver the same outcome cheaper.*
```
    My target clients currently pay [SERVICE PROVIDER] approximately [AMOUNT] for [OUTCOME]. (1) What would it cost me to deliver that same outcome using AI-assisted processes internally? (2) What price point undercuts the current provider while still being profitable for me? (3) What data will I collect from the first 3-5 clients that would let me automate further?
```

**Prompt 5: Revenue Share Calculator What it solves:** *Deciding whether to take cash upfront or bet on a bigger backend deal.*
```
    I am considering a revenue share arrangement with [CLIENT/PARTNER] for [PROJECT]. (1) Can I survive financially if this project pays nothing for 6 months? (2) What is the expected upside if it succeeds, compared to what I would charge hourly? (3) What negotiating position am I in, and what would I need to demonstrate before proposing a revenue share?
```

**Prompt 6: 30-Day Content Plan What it solves:** *Creating content that attracts clients instead of just followers.*
```
    I work in [YOUR INDUSTRY]. My target client is [DESCRIBE THEM]. Help me design a 30-day content plan that demonstrates my expertise in [YOUR SPECIFIC SKILL]. Give me 10 specific video topics with titles. Each one should teach something concrete and position me as someone who thinks differently about [YOUR INDUSTRY]. Keep production requirements minimal. Phone camera, no editing.
```

**Prompt 7: Problem-First AI Mapping What it solves:** *Cutting through AI noise and figuring out which tools actually matter for your business.*
```
    I work in [MY INDUSTRY]. Here are my three biggest operational problems right now, described without any reference to technology: [LIST THEM]. For each problem, (1) What features exist in AI, in traditional software, or in better process that could solve part of it? (2) Which solution gives me the fastest outcome with the least investment? (3) What is something my industry has never been able to offer before that becomes possible when these problems are solved?
```

**Prompt 8: Full Business Audit What it solves:** *Running the whole framework sequence in one pass. Takes longer but covers the most ground.*
```
    I run [YOUR BUSINESS] in [YOUR INDUSTRY]. My monthly revenue is roughly [AMOUNT]. My biggest problems are [LIST 2-3]. My target clients are [DESCRIBE THEM]. They currently solve these problems by [PAYING X / DOING Y / IGNORING IT]. Walk me through each of these steps: (1) What is the cheapest fix I could implement this week? (2) Could I sell my manual solution as a service? What would I charge? (3) Where will that service break at scale? (4) Who in my market currently pays the most to solve this problem, and what do they pay? (5) What content could I create that would attract those buyers? Give me specific video titles. (6) At what point should I consider building software, and what should it do?
```