import {ingredientAmount,formatIngredient,validateSettings} from './recipe-logic.mjs';
import {cookText} from './display-units.mjs';
const escape=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
/** Reject incomplete allocation trees instead of silently dropping ingredients from a diagram. */
export function validateFlow(recipe){
 if(!recipe.flow?.root?.children?.length)throw new Error(`Missing TRN flow: ${recipe.id}`);
 const allocations=new Map();const seen=new Set();
 function visit(node){
  if(seen.has(node))throw new Error('Cyclic/reused TRN node');seen.add(node);
  if(node.children){if(!node.action||!node.children.length)throw new Error('Empty operation');node.children.forEach(visit);return;}
  if(!recipe.ingredients.some(i=>i.id===node.ingredientId))throw new Error(`Unknown TRN ingredient ${node.ingredientId}`);
  const list=allocations.get(node.ingredientId)||[];list.push(node);allocations.set(node.ingredientId,list);
  if(node.share&&!['pinch','remainder'].includes(node.share))throw new Error('Unknown symbolic allocation');
  if(!node.share&&(!(Number(node.fraction??1)>0)||Number(node.fraction??1)>1))throw new Error('Invalid ingredient fraction');
 }
 visit(recipe.flow.root);
 for(const i of recipe.ingredients){const parts=allocations.get(i.id);if(!parts)throw new Error(`Unallocated ${i.id}`);
  if(parts.some(p=>p.share)){if(parts.length!==2||!parts.some(p=>p.share==='pinch')||!parts.some(p=>p.share==='remainder'))throw new Error(`Unbalanced symbolic allocation ${i.id}`);}
  else if(Math.abs(parts.reduce((sum,p)=>sum+Number(p.fraction??1),0)-1)>1e-9)throw new Error(`Unbalanced allocation ${i.id}`);
 }
 return true;
}
/** Compute a contiguous-row dependency graph. Children extend to their consuming column. */
export function flowGrid(recipe,settings={}){
 validateFlow(recipe);const {servings,units}=validateSettings(settings);const leaves=[];const operations=[];
 function walk(node,parent=null){
  const item={...node,parent,start:leaves.length};
  if(!node.children){item.depth=0;item.rows=1;const ingredient=recipe.ingredients.find(i=>i.id===node.ingredientId);
   const amount=ingredientAmount(ingredient,servings)*Number(node.fraction??1);
   const total=formatIngredient(ingredient,servings,units);
   item.quantity=node.share==='pinch'?`Small pinch from ${total}`:node.share==='remainder'?`Remainder of ${total}`:formatIngredient({...ingredient,amount,us:ingredient.us?{...ingredient.us,amount:ingredient.us.amount*amount/ingredient.amount}:undefined,scale:'fixed'},4,units);
   item.name=ingredient.name;item.state=cookText(ingredient.state||'',units);leaves.push(item);return item;
  }
  item.children=node.children.map(child=>walk(child,item));item.depth=1+Math.max(...item.children.map(child=>child.depth));item.rows=leaves.length-item.start;item.action=cookText(node.action,units);operations.push(item);return item;
 }
 function compact(node){
  if(!node.children)return {...node};
  const children=node.children.map(compact);
  if(children.length===1&&children[0].children)return {action:children[0].action+' Then: '+node.action,children:children[0].children};
  return {...node,children};
 }
 const root=walk(compact(recipe.flow.root));const rows=leaves.map(leaf=>({ingredient:leaf,cells:[{kind:'ingredient',col:0,colspan:leaf.parent.depth,rowspan:1,text:leaf.quantity,name:leaf.name,state:leaf.state,essentialState:/raw|thaw|fully cooked|drain|shelf-stable|package weight|jarred|squeeze-bottle/i.test(leaf.state)}]}));
 for(const op of operations)rows[op.start].cells.push({kind:'operation',col:op.depth,colspan:op.parent?op.parent.depth-op.depth:1,rowspan:op.rows,text:op.action});
 rows.forEach(r=>r.cells.sort((a,b)=>a.col-b.col));
 return {prep:recipe.flow.prep.map(t=>cookText(t,units)),columns:root.depth+1,rows};
}
export function flowHtml(recipe,settings={}){
 return gridHtml(recipe.title,flowGrid(recipe,settings));
}
export function gridHtml(title,grid){
 return `<div class="trn-scroll" tabindex="0" role="region" aria-label="${escape(title)} cooking flow, scroll horizontally"><table class="trn-table"><caption>${escape(title)} · ingredient-to-operation cooking flow</caption><tbody>${grid.prep.map(t=>`<tr><td colspan="${grid.columns}" class="trn-prep">${escape(t)}</td></tr>`).join('')}${grid.rows.map(r=>`<tr>${r.cells.map(c=>c.kind==='ingredient'?`<th scope="row" colspan="${c.colspan}" class="trn-ingredient"><strong>${escape(c.text)}</strong> ${escape(c.name)}<small class="${c.essentialState?'trn-state-essential':'trn-state-detail'}">${escape(c.state)}</small></th>`:`<td rowspan="${c.rowspan}" colspan="${c.colspan}" class="trn-operation">${escape(c.text)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
}
