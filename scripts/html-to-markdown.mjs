import TurndownService from 'turndown';
import { load } from 'cheerio';
import { imageUrl } from '../src/lib/html.ts';

const converter = new TurndownService({
  headingStyle: 'atx', bulletListMarker: '-', codeBlockStyle: 'fenced',
  preformattedCode: true,
  blankReplacement: (_content, node) => node.attributes?.length || /^H[1-6]$/u.test(node.nodeName) ? `\n\n${node.outerHTML}\n\n` : '\n\n',
});
const escapeMarkdown = converter.escape.bind(converter);
converter.escape = text => escapeMarkdown(text).replace(/&/gu, '&amp;').replace(/</gu, '\\<').replace(/>/gu, '\\>');
// These containers carry author formatting or media that Markdown cannot model.
// Keep their complete subtree instead of converting descendants and losing attrs.
converter.addRule('preserveHtml', {
  filter: node => ['TABLE', 'FIGURE', 'IFRAME', 'VIDEO', 'SOURCE', 'PRE', 'CODE', 'STRONG', 'B', 'EM', 'I', 'UL', 'OL', 'BLOCKQUOTE'].includes(node.nodeName)
    || node.hasAttribute('style') || node.hasAttribute('id') || node.hasAttribute('class')
    || (node.nodeName === 'A' && node.hasAttribute('target'))
    || (node.nodeName === 'IMG' && (node.hasAttribute('width') || node.hasAttribute('height'))),
  replacement: (_content, node) => node.isBlock ? `\n\n${node.outerHTML}\n\n` : node.outerHTML,
});
converter.keep(['s', 'del', 'ins', 'sub', 'sup']);
converter.addRule('removeExecutable', { filter: ['script', 'style'], replacement: () => '' });

export function htmlToMarkdown(html) {
  const $ = load(html, {}, false);
  $('script, style').remove();
  $('img').each((_index, node) => { $(node).attr('src', imageUrl($(node).attr('src') ?? '')); });
  return converter.turndown($.html());
}
