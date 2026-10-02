import { readFile, readdir } from 'node:fs/promises';
import { parseAllDocuments } from 'yaml';

async function check(directory) {
  for (const file of await readdir(directory, { withFileTypes: true })) {
    const path = `${directory}/${file.name}`;
    if (file.isDirectory() && directory.startsWith('.github')) await check(path);
    else if (file.isFile() && /\.ya?ml$/u.test(file.name)) {
      for (const document of parseAllDocuments(await readFile(path, 'utf8'), { uniqueKeys: true })) {
        if (document.errors.length) throw new Error(`${path}: ${document.errors.join('\n')}`);
      }
    }
  }
}
await check('.');
await check('.github');
process.stdout.write('YAML syntax and duplicate-key validation passed.\n');
