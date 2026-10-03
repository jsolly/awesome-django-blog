import { defineConfig } from 'astro/config';
import svelte from '@astrojs/svelte';
import tailwindcss from '@tailwindcss/vite';
import { satteri } from '@astrojs/markdown-satteri';
import recipePwa from './scripts/recipes/pwa-build.mjs';

export default defineConfig({
  site: 'https://www.blogthedata.com',
  output: 'static',
  trailingSlash: 'always',
  prerenderConflictBehavior: 'error',
  integrations: [svelte(), recipePwa()],
  vite: { plugins: [tailwindcss()] },
  markdown: { syntaxHighlight: 'prism', processor: satteri({ features: { smartPunctuation: false, gfm: false } }) },
  security: {
    csp: {
      directives: [
        "default-src 'self'", "img-src 'self' https: data:", "font-src 'self'",
        "connect-src 'self'", "object-src 'none'", "base-uri 'self'", "form-action 'self'",
        'frame-src https://www.youtube.com https://www.youtube-nocookie.com https://viewer.diagrams.net https://nbviewer.org',
      ],
      styleDirective: { resources: [{ resource: "'self'", kind: 'element' }, { resource: "'unsafe-inline'", kind: 'attribute' }] },
    },
  },
  server: { host: '127.0.0.1', port: 4321 },
});
