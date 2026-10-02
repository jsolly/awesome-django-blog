import sanitizeHtml from 'sanitize-html';
import { decodeHTML } from 'entities';

export const legacyMedia = 'https://d1d7p8ufhgz4ld.cloudfront.net/media/';

export function imageUrl(path: string) {
  if (!path || path === 'default.webp') return '/media/default.webp';
  if (/^https:\/\//u.test(path) || path.startsWith('/media/')) return path;
  return `${legacyMedia}${path.replace(/^\/?mediafiles\//u, '')}`;
}

export function plainText(html: string) {
  return decodeHTML(sanitizeHtml(html, { allowedTags: [], allowedAttributes: {} })).replace(/\s+/gu, ' ').trim();
}

export function articleHtml(body: string) {
  const headingIds = new Set<string>();
  const rendered = sanitizeHtml(body, {
    allowedTags: [...sanitizeHtml.defaults.allowedTags, 'img', 'iframe', 'del', 'video', 'source'],
    allowedAttributes: {
      '*': ['id', 'class', 'style'], a: ['href', 'title', 'target', 'rel'],
      img: ['src', 'alt', 'width', 'height', 'loading', 'decoding'],
      iframe: ['src', 'title', 'width', 'height', 'allow', 'allowfullscreen', 'loading'],
      td: ['colspan', 'rowspan'], th: ['colspan', 'rowspan', 'scope'],
      code: ['class'], ol: ['start'], video: ['src', 'controls', 'poster'], source: ['src', 'type'],
    },
    allowedSchemes: ['https', 'http', 'mailto'],
    allowedIframeHostnames: ['www.youtube.com', 'www.youtube-nocookie.com', 'viewer.diagrams.net', 'nbviewer.org'],
    allowedStyles: {
      '*': {
        width: [/^(?:0|\d+(?:\.\d+)?(?:%|px|em|rem))$/u], height: [/^(?:0|\d+(?:\.\d+)?(?:%|px|em|rem))$/u],
        'min-width': [/^\d+(?:\.\d+)?(?:%|px|em|rem)$/u],
        'aspect-ratio': [/^\d+\s*\/\s*\d+$/u],
        'text-align': [/^(?:left|right|center|justify|start)$/u], float: [/^(?:left|right|none)$/u],
        'background-color': [/^(?:#[0-9a-f]{3,8}|(?:rgb|hsl)\([\d.,%\s]+\))$/iu],
        color: [/^(?:#[0-9a-f]{3,8}|(?:rgb|hsl)\([\d.,%\s]+\))$/iu],
        position: [/^(?:relative|absolute)$/u], top: [/^0$/u], left: [/^0$/u],
        'padding-bottom': [/^\d+(?:\.\d+)?(?:%|px|em|rem)$/u],
        padding: [/^(?:\d+(?:\.\d+)?(?:px|em|rem)\s*){1,4}$/u],
        'margin-left': [/^(?:0|\d+(?:\.\d+)?(?:px|em|rem))$/u],
        border: [/^\d+px solid (?:black|#[0-9a-f]{3,8})$/iu],
        'border-color': [/^#[0-9a-f]{3,8}$/iu], 'border-style': [/^solid$/u],
        'border-collapse': [/^collapse$/u], 'overflow-x': [/^auto$/u],
        'font-family': [/^[a-z\s,-]+$/iu], 'font-size': [/^\d+(?:\.\d+)?(?:px|em|rem)$/u],
        'font-weight': [/^[1-9]00$/u], 'line-height': [/^\d+(?:\.\d+)?$/u],
        'list-style-type': [/^disc$/u],
        display: [/^inline(?:\s*!important)?$/u], 'font-style': [/^normal$/u],
        'font-variant-caps': [/^normal$/u], 'font-variant-ligatures': [/^normal$/u],
        'letter-spacing': [/^normal$/u], 'white-space': [/^normal$/u],
        'text-transform': [/^none$/u], 'text-indent': [/^0px$/u], 'word-spacing': [/^0px$/u],
        'text-decoration-color': [/^initial$/u], 'text-decoration-style': [/^initial$/u],
        'text-decoration-thickness': [/^initial$/u], '-webkit-text-stroke-width': [/^0px$/u],
        orphans: [/^2$/u], widows: [/^2$/u],
      },
    },
    transformTags: {
      img: (_tag, attrs) => ({ tagName: 'img', attribs: { ...attrs, src: imageUrl(attrs.src ?? ''), loading: 'lazy', decoding: 'async' } }),
      iframe: (_tag, attrs) => ({ tagName: 'iframe', attribs: { ...attrs, title: attrs.title || 'Embedded article content', loading: 'lazy' } }),
      a: (_tag, attrs) => ({ tagName: 'a', attribs: { ...attrs, rel: 'noopener noreferrer' } }),
    },
  }).replace(/<(h[1-3])([^>]*)>([\s\S]*?)<\/\1>/gu, (_match: string, tag: string, attrs: string, text: string) => {
    const id = headingId(plainText(text));
    headingIds.add(id);
    const attributes = attrs.replace(/\s+id="[^"]*"/gu, '');
    return `<${tag}${attributes} id="${id}">${text}<a class="heading-link" href="#${id}" aria-label="Link to this heading">#</a></${tag}>`;
  });
  return rendered.replace(/<([a-z][a-z0-9]*)([^>]*)>/gu, (match: string, tag: string, attributes: string) => {
    if (/^h[1-3]$/u.test(tag)) return match;
    return `<${tag}${attributes.replace(/\s+id="([^"]*)"/gu, (attribute: string, id: string) => headingIds.has(id) ? '' : attribute)}>`;
  });
}

export function headingId(text: string) {
  return text.trim().toLowerCase().replace(/\s+/gu, '-').replace(/[^a-zA-Z0-9_-]/gu, '');
}

export function xml(value: string) {
  return value.replace(/[<>&"']/gu, character => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;', "'": '&apos;' })[character] ?? character);
}
