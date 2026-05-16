# 4.4 Making Claude Understand your Project

## What You'll Get From This
You will write a CLAUDE.md file that makes Claude Code behave like it has been on your project for a month. One file. Ten minutes. The difference is immediate.

## The Lesson
**One file changes everything**
In Session 1 you installed Claude Code. In Session 2 you used it on real tasks. In Session 3 you used Desktop for thinking. All of that worked. But there is a problem you have probably already noticed: Claude Code does not know your project.

It does not know your conventions. It does not know your file structure. It does not know which libraries you use, which commands to run, or what you consider good work. Every time you start a new conversation, Claude is a smart stranger. It can do the work, but it guesses at all the things a team member would already know.

The fix is one file: **CLAUDE.md**.

## What a CLAUDE.md is
A markdown file that sits in the root of your project folder. Claude Code reads it automatically every time it starts. It tells Claude what this project is, how it works, and what matters. Think of it as an onboarding document for a new hire. Except the new hire reads the entire thing in two seconds and follows every word.

## Before vs After
Run the same task on the same project. First without a CLAUDE.md. Then with one. The difference:

Without CLAUDE.mdWith CLAUDE.mdGeneric code styleMatches your conventionsGuesses at file structureKnows where things liveDoes not know your commandsRuns your actual test suiteSuggests wrong librariesUses your dependencies

This is the same principle from Section 1.2: structured context changes the output. The CLAUDE.md is a more focused, project-specific version of the identity and context files you set up in Section 1. If you skipped Section 1 and jumped straight to Section 4, this lesson still works. But go back to 1.2 afterward to understand the bigger picture.

[📌 JAKE: The before/after demo is the most important visual in this lesson. Same task, same project. Show the generic output without CLAUDE.md, then the specific output with it. Side by side if possible.]

## What goes in it
Five things. Keep it short. 15 lines is enough. 10 minutes to write.

1. **Project overview** — Two to three sentences. What is this? What does it do?
2. **Tech stack** — What languages, frameworks, databases, tools.
3. **How to run things** — Dev server, tests, build commands. The commands Claude needs to know.
4. **Key conventions** — Naming patterns, file structure, architectural patterns you follow.
5. **What to avoid** — Things Claude should not do. Libraries you do not use. Patterns you have moved away from.

## Example CLAUDE.md
```
# My Web App

React 18 + Express + PostgreSQL + TypeScript

## Commands
npm run dev | npm run api | npm test

## Conventions
Functional components only. Routes in src/api/. 
All database queries go through src/db/queries/.

## Avoid
No class components. Don't modify db/migrations directly.
Don't use Moment.js (we use date-fns).
```

That is it. Fifteen lines. Ten minutes. The difference in Claude's behavior is immediate.

## Tips
**Write it for a smart person who just joined your project.** That is literally what Claude is. If a new team member would need to know it on day one, put it in the CLAUDE.md.

**Update it when your project changes.** The CLAUDE.md is a living document. When you add a new convention, change a library, or shift your architecture, update the file. This is the same advice from 3.3 (Common Mistakes): stale context files are the most common reason Claude starts "getting worse."

**Do not overthink it.** A mediocre CLAUDE.md beats no CLAUDE.md every time. You can always improve it later. The first version takes 10 minutes. Each edit takes 30 seconds. Start now.

**This is not just for code projects.** If your project is a folder full of documents, the CLAUDE.md describes what those documents are, how they are organized, and what you are using them for. The same principle applies to any structured folder, whether it contains code, writing, research, or client files.

## Write your CLAUDE.md
Do this now.

1. Pick a project. Work project, side project, or even a document folder.
2. Create a file called CLAUDE.md in the root of the folder.
3. Fill it in using the template:
```
# [Project Name]

## Overview
[2-3 sentences. What is this? What does it do?]

## Tech Stack
[Languages, frameworks, tools. Or "document types" if not a code project.]

## Commands
[Dev, test, build. Or "how to use these files" if not code.]

## Conventions
[Patterns, naming, structure.]

## Avoid
[Things Claude should not do.]
```

4. Save it. Open Claude Code in the folder. Run a task.
5. (Optional) Temporarily move the CLAUDE.md out of the folder. Run the same task. Compare the outputs. Move it back.

The comparison is what makes the value click. You will not go back.