import { load } from 'cheerio';

const normalize = text => text.replace(/\s+/gu, ' ').trim();
const blockTags = new Set(['p', 'div', 'figure', 'figcaption', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'ul', 'ol', 'blockquote', 'tr', 'td', 'th', 'pre', 'hr', 'br']);
function visibleText(node) {
  if (node.type === 'text') return node.data;
  const text = (node.children ?? []).map(visibleText).join('');
  return blockTags.has(node.name) ? ` ${text} ` : text;
}

// A representation of rendered meaning, independent from the converter. It
// accepts harmless HTML/Markdown differences (b/strong, i/em, whitespace outside
// pre) while preserving order, hierarchy, spans and exact preformatted text.
export function articleSignature(html) {
  const $ = load(html, {}, false);
  $('.heading-link, script, style').remove();
  const select = (selector, inspect) => $(selector).toArray().map(node => inspect($(node), node));
  const attrs = (node, names) => Object.fromEntries(names.map(name => [name, node.attr(name) ?? '']));
  const list = node => ({
    type: node.name,
    start: $(node).attr('start') ?? '1',
    items: $(node).children('li').toArray().map(item => {
      const copy = $(item).clone(); copy.find('ul, ol').remove();
      return { text: normalize(visibleText(copy[0])), lists: $(item).children('ul, ol').toArray().map(list) };
    }),
  });
  return {
    text: normalize(visibleText($.root()[0])),
    headings: select('h1,h2,h3,h4,h5,h6', (element, node) => ({ level: node.name, text: normalize(element.text()), id: element.attr('id') ?? '' })),
    links: select('a', element => ({ text: normalize(element.text()), ...attrs(element, ['href', 'title', 'target']) })),
    images: select('img', element => attrs(element, ['src', 'alt', 'width', 'height'])),
    embeds: select('iframe,video,source', (element, node) => ({ type: node.name, ...attrs(element, ['src', 'title', 'width', 'height', 'allow', 'allowfullscreen', 'controls', 'poster', 'type']) })),
    lists: $('ul,ol').filter((_index, node) => !$(node).parents('ul,ol').length).toArray().map(list),
    quotes: select('blockquote', element => normalize(visibleText(element[0]))),
    emphasis: select('strong,b,em,i,s,del,ins,sub,sup', (element, node) => ({ type: ({ b: 'strong', i: 'em', s: 'del' })[node.name] ?? node.name, text: normalize(element.text()) })),
    code: select('code', element => element.text()),
    pre: select('pre', element => element.text()),
    tables: select('table', element => element.find('tr').toArray().map(row => $(row).children('td,th').toArray().map(cell => ({ type: cell.name, text: normalize(visibleText(cell)), colspan: $(cell).attr('colspan') ?? '1', rowspan: $(cell).attr('rowspan') ?? '1' })))),
    styles: select('[style]', (element, node) => ({ type: node.name, style: (element.attr('style') ?? '').replace(/\s+/gu, '').replace(/;$/u, '') })),
  };
}
