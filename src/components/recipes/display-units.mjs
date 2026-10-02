import {temperature} from './recipe-logic.mjs';
const fractions={'¼':.25,'½':.5,'¾':.75,'⅛':.125};
function inches(value){const match=value.match(/^(\d*)([¼½¾⅛])?$/);return match?Number(match[1]||0)+(fractions[match[2]]||0):Number(value);}
/** Convert display geometry only. Preserve the original setting and safe endpoint. */
export function cookText(text,units='us'){
 if(units!=='metric')return text;
 return text.replace(/(\d+)°F/g,(_,f)=>temperature(Number(f),'metric',[145,160,165].includes(Number(f))))
 .replace(/(\d+(?:\.\d+)?[¼½¾⅛]?|[¼½¾⅛])×(\d+(?:\.\d+)?[¼½¾⅛]?|[¼½¾⅛])(?:-inch| inches)/g,(original,a,b)=>`${Number((inches(a)*2.54).toFixed(2))}×${Number((inches(b)*2.54).toFixed(2))} cm (${original})`)
 .replace(/(?<![\d×])(?:\d+(?:\.\d+)?[¼½¾⅛]?|[¼½¾⅛])(?:-inch| inches| inch)\b/g,(original)=>{if(original.includes('×'))return original;const value=original.split(/[- ]/)[0];return `${Number((inches(value)*2.54).toFixed(2))} cm (${original})`;});
}
