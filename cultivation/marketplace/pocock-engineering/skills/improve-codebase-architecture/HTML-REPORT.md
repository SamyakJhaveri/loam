# HTML Report Format

Self-contained HTML file using Tailwind CSS and Mermaid diagrams, stored in the OS temp directory.

## Scaffold

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Architecture Review — {repo-name}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
    mermaid.initialize({ startOnLoad: true, theme: 'neutral' });
  </script>
</head>
<body class="bg-gray-50 text-gray-900 max-w-5xl mx-auto px-6 py-10">

  <header class="mb-10">
    <h1 class="text-3xl font-bold">{repo-name} — Architecture Review</h1>
    <p class="text-gray-500 mt-1">{date}</p>
    <div class="flex gap-3 mt-4 text-sm">
      <span class="px-2 py-1 bg-green-100 text-green-800 rounded">Strong</span>
      <span class="px-2 py-1 bg-yellow-100 text-yellow-800 rounded">Worth exploring</span>
      <span class="px-2 py-1 bg-gray-100 text-gray-600 rounded">Speculative</span>
    </div>
  </header>

  <!-- Candidate cards go here -->

  <section class="mt-12 p-6 bg-blue-50 rounded-lg">
    <h2 class="text-xl font-bold">Top Recommendation</h2>
    <p class="mt-2">{which candidate to tackle first and why}</p>
  </section>

</body>
</html>
```

## Candidate Card Template

```html
<article class="bg-white rounded-lg shadow p-6 mb-6">
  <div class="flex items-center justify-between mb-4">
    <h2 class="text-xl font-semibold">{title}</h2>
    <span class="px-2 py-1 bg-{color}-100 text-{color}-800 rounded text-sm">{strength}</span>
  </div>

  <p class="text-sm text-gray-500 font-mono mb-3">{file list}</p>

  <div class="mb-4">
    <p><strong>Problem:</strong> {one sentence}</p>
    <p><strong>Solution:</strong> {one sentence}</p>
  </div>

  <div class="grid grid-cols-2 gap-4 mb-4">
    <div>
      <h3 class="font-medium text-red-700 mb-2">Before</h3>
      <pre class="mermaid">{mermaid diagram or hand-built SVG}</pre>
    </div>
    <div>
      <h3 class="font-medium text-green-700 mb-2">After</h3>
      <pre class="mermaid">{mermaid diagram or hand-built SVG}</pre>
    </div>
  </div>

  <ul class="text-sm space-y-1">
    {bullet-point wins, ≤6 words each}
  </ul>
</article>
```

## Diagram Guidelines

- Use Mermaid for dependency flows, call graphs, sequences
- Use hand-built SVG/CSS for mass diagrams, cross-sections, nested boxes
- Mix both freely — variety makes the report readable
- Before/After diagrams are the centerpiece of each card

## Language Rules

- Use only: module, interface, implementation, depth, deep, shallow, seam, adapter, leverage, locality
- Do NOT use: component, API, layer, wrapper, service, boundary (when the LANGUAGE.md terms apply)
- Plain English, concise. No hedging.
