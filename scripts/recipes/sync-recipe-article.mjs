import fs from 'node:fs';
import assert from 'node:assert/strict';
import {flowHtml} from '../../src/components/recipes/trn-logic.mjs';
import {formatIngredient} from '../../src/components/recipes/recipe-logic.mjs';
const root=new URL('../../src/components/recipes/',import.meta.url);
const file=new URL('../../src/content/posts/15-minute-dump-and-go-instant-pot-recipes.md',import.meta.url);
const data=JSON.parse(fs.readFileSync(new URL('recipes.json',root),'utf8'));
let article=fs.readFileSync(file,'utf8');
function ingredientLine(i){const us=formatIngredient(i,4,'us');const metric=formatIngredient(i,4,'metric');return `- ${us}${metric!==us?' ('+metric+')':''} ${i.name}${i.state?' — '+i.state:''}${i.note?'. '+i.note:''}`;}
function section(r){
 const lines=[`### ${r.title}`,`About ${r.activeMinutes} minutes hands-on; ${r.totalMin}–${r.totalMax} minutes${r.timeVariable?' expected':''} total. Four adult servings. ${r.summary}`,'**Cooking flow · Tabular Recipe Notation**',flowHtml(r,{servings:4,units:'us'}),'**Ingredients**',r.ingredients.map(ingredientLine).join('\n'),'**Equipment and capacity**',r.equipment.map(x=>'- '+x).join('\n'),'**Method**',r.steps.map((s,i)=>`${i+1}. **${s.title}.** ${s.text}`).join('\n')];
 if(r.familyOptions.length)lines.push('**Family add-on**',r.familyOptions.map(o=>`- Per non-keto adult: ${formatIngredient({...o,scale:'fixed'},4,'us')}${o.unit==='g'?' ('+o.amount+' g)':''} ${o.ingredientName}. ${o.note}`).join('\n'));
 lines.push('**Why it works**',r.flavorRationale,r.tips.map(x=>'- '+x).join('\n'));
 if(r.fallback)lines.push('**Capacity fallback**',r.fallback);
 lines.push('**First-cook checks and limits**',r.limitations.map(x=>'- '+x).join('\n'),'**Sources**',r.sources.map(s=>`- [${s.title}](${s.url})`).join('\n'),'These sources support safety, labels or comparable cooking methods; this exact recipe has not been kitchen-tested.');
 if(r.image)lines.splice(1,0,`<figure class="recipe-illustration"><img src="${r.image.src}" width="${r.image.width}" height="${r.image.height}" srcset="${r.image.detailSrcset}" sizes="(max-width:600px) 340px, 640px" alt="${r.image.alt}" loading="lazy" decoding="async" /><figcaption>${r.image.caption}</figcaption></figure>`);
 return lines.filter(Boolean).join('\n\n')+'\n\n';
}
for(const r of data.recipes){const escaped=r.title.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');const pattern=new RegExp('^### '+escaped+'\\n[\\s\\S]*?(?=^### |^## |(?![\\s\\S]))','m');if(!pattern.test(article))throw new Error('Missing recipe heading: '+r.title);article=article.replace(pattern,()=>section(r));}
article=article.replace(/^excerpt:.*$/m,'excerpt: "Twelve low-attention dinners with diet and appliance filters, serving scaling, unit conversions and separate family starches."');
// Raw HTML tables remain readable with the migration app's GFM-disabled parser.
const escapeHtml=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
const inline=s=>escapeHtml(s).replace(/\[([^\]]+)\]\(([^)]+)\)/g,'<a href="$2">$1</a>').replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>');
article=article.replace(/^(\|[^\n]+\|\n)\|[ :|\-]+\|\n((?:\|[^\n]+\|(?:\n|$))+)/gm,(_,head,body)=>{
 const cells=line=>line.trim().slice(1,-1).split('|').map(x=>inline(x.trim()));
 return '<table>\n<thead><tr>'+cells(head).map(x=>'<th scope="col">'+x+'</th>').join('')+'</tr></thead>\n<tbody>\n'+body.trim().split('\n').map(row=>'<tr>'+cells(row).map(x=>'<td>'+x+'</td>').join('')+'</tr>').join('\n')+'\n</tbody>\n</table>\n';
});
// Derive all comparison tables from the same formulas used by the interactive UI.
const mealLink=r=>({html:`<a href="#${escapeHtml(r.id)}">${escapeHtml(r.title)}</a>`});
const cell=x=>x&&typeof x==='object'&&'html' in x?x.html:escapeHtml(String(x));
const table=(headers,rows)=>'<table>\n<thead><tr>'+headers.map(x=>'<th scope="col">'+cell(x)+'</th>').join('')+'</tr></thead>\n<tbody>\n'+rows.map(row=>'<tr>'+row.map(x=>'<td>'+cell(x)+'</td>').join('')+'</tr>').join('\n')+'\n</tbody>\n</table>';
const overview=table(['Meal','Group','Appliance','Hands-on min','Total min','Attention and finish checks'],data.recipes.map(r=>[mealLink(r),{keto:'Keto',shared:'Keto + family',nonketo:'Non-keto'}[r.group],r.key==='potato_chicken'?'Microwave + oven':{'air-fryer':'Two air fryers',oven:'Oven','instant-pot':'Instant Pot'}[r.appliance],r.activeMinutes,`${r.totalMin}–${r.totalMax}${r.timeVariable?' expected':''}`,r.attentionSummary]));
const nutrition=table(['Meal, one quarter of recipe','kcal','Protein g','Total carbs g','Fiber g','Net carbs g'],data.recipes.map(r=>[mealLink(r),Math.round(r.nutrition.kcal),r.nutrition.protein_g.toFixed(1),r.nutrition.carbs_g.toFixed(1),r.nutrition.fiber_g.toFixed(1),r.nutrition.net_carbs_g.toFixed(1)]));
const options=[...new Map(data.recipes.flatMap(r=>r.familyOptions).map(o=>[o.id,o])).values()];
const addons=table(['One family add-on per person','Approx kcal added','Total carbs g added','Fiber g added','Net carbs g added'],options.map(o=>[`${formatIngredient({...o,scale:'fixed'},4,'metric')} ${o.ingredientName}`,Math.round(o.nutrition.kcal),o.nutrition.carbs_g.toFixed(1),o.nutrition.fiber_g.toFixed(1),o.nutrition.net_carbs_g.toFixed(1)]));
let tableIndex=0;const tables=[overview,nutrition,addons];
article=article.replace(/<table>[\s\S]*?<\/table>/g,()=>{if(tableIndex>=tables.length)throw new Error('Unexpected article table');return tables[tableIndex++];});
if(tableIndex!==3)throw new Error('Expected overview, nutrition and family tables');
article=article.replace(/(?<!<div class="recipe-table-scroll">\n)<table>[\s\S]*?<\/table>/g,table=>'<div class="recipe-table-scroll">\n'+table+'\n</div>');
if(process.argv.includes('--check')) assert.equal(fs.readFileSync(file,'utf8'),article,'Run npm run recipes:sync to update the complete recipe article.');
else fs.writeFileSync(file,article);
console.log('Complete recipe article matches canonical recipes.json.');
