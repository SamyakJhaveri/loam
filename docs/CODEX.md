# Codex while developing Loam

Start a fresh Loam session with `bin/codex-loam`. The launcher disables the
Superpowers plugin and the separately installed shared Superpowers skills for
that invocation. It preserves the model, permissions, native execution rules,
and other configuration. Planning, subagents, reviews, and tests remain
available through Codex; their use is no longer prescribed by those skills.

For a comparison during normal work, use `bin/codex-loam --superpowers`.
This sets the plugin to enabled while keeping the duplicate shared copies disabled.
Use a fresh session and a comparable task. Judge completion quality, requests
to reapprove authorized work, and repeated work. Keep repository checks.

Ordinary `codex` and app launches keep their existing setup. Resuming a chat
can retain instructions already loaded, so a fresh chat is needed for a clean
comparison. The launcher forwards remaining arguments to Codex. Its
`skills.config` override replaces that array for this invocation; merge any
future personal per-skill overrides before relying on them with this launcher.

The launcher stays outside `seed/`; generated projects and global files are
unchanged. Root `.codex` still points at the seed configuration. In the
installed client, project-level skill-disable entries remained enabled in
`skills/list`; launch overrides disabled them in that native API.
Checks verified effective configuration and shared-skill enablement in a
temporary Codex home. Loading the installed plugin in a fresh normal session
remains unverified. These checks do not establish quality gains or token savings.

Basis: [Astra guidance](https://developers.openai.com/api/docs/guides/latest-model#prompting-best-practices)
on instruction conflicts and excessive process; [Codex customization](https://learn.chatgpt.com/docs/customization/overview)
on small persistent instructions; [skill controls](https://learn.chatgpt.com/docs/build-skills)
and [configuration overrides](https://learn.chatgpt.com/docs/config-file/config-reference).
