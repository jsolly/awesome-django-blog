import {readFileSync,mkdirSync,writeFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import {recipeBundle,documentMarkdown} from '../../src/components/recipes/recipe-export.mjs';
const {recipes}=JSON.parse(readFileSync(new URL('../../src/components/recipes/recipes.json',import.meta.url),'utf8'));
const bundle=recipeBundle(recipes,{servings:4,units:'us',familyDiners:0});
const root=new URL('../../public/data/',import.meta.url);if(!process.argv.includes('--check'))mkdirSync(root,{recursive:true});
function writeGenerated(file,content){
 if(process.argv.includes('--check'))assert.equal(readFileSync(file,'utf8'),content,'Run npm run recipes:sync to update assistant downloads.');
 else writeFileSync(file,content);
}
writeGenerated(new URL('recipe-library.json',root),JSON.stringify(bundle,null,2)+'\n');
writeGenerated(new URL('recipe-library.md',root),`# Easy Meals recipe library\n\n${recipes.length} complete four-serving recipes. Keto bases are shown without family starch; separate measured per-person options are included below each shared recipe. Small seasoning amounts use spoon measures. Recipes are newly designed and not kitchen-tested.\n\n`+bundle.recipes.map(d=>documentMarkdown(d,2)).join('\n---\n\n'));
console.log('Synchronized assistant JSON and Markdown.');
