/** Pure calculations for the meal library. Recipe ingredient amounts are for four adults. */
const BASE_SERVINGS = 4;
const SERVINGS = new Set([2, 4, 6, 8]);
const NUTRIENTS = ['kcal', 'protein_g', 'carbs_g', 'fiber_g', 'net_carbs_g'];

const finite = (value) => typeof value === 'number' && Number.isFinite(value);
const clean = (value) => String(value ?? '').trim().toLocaleLowerCase();

export function validateSettings(settings = {}) {
  const servings = SERVINGS.has(Number(settings?.servings)) ? Number(settings.servings) : BASE_SERVINGS;
  const familyDiners = Number.isInteger(Number(settings?.familyDiners))
    ? Math.max(0, Math.min(servings, Number(settings.familyDiners)))
    : 0;
  const units = settings?.units === 'metric' ? 'metric' : 'us';
  return { servings, familyDiners, units };
}

/** Use familiar fractions for kitchen measures; retain two decimals otherwise. */
export function formatQuantity(value) {
  if (!finite(value)) return '—';
  if (value === 0) return '0';
  const sign = value < 0 ? '−' : '';
  const magnitude = Math.abs(value);
  if (magnitude >= 10) return sign + Number(magnitude.toFixed(2)).toString();
  const whole = Math.floor(magnitude + 1e-9);
  const remainder = magnitude - whole;
  const fractions = [
    [0, ''], [1 / 8, '⅛'], [1 / 6, '⅙'], [1 / 4, '¼'], [1 / 3, '⅓'],
    [3 / 8, '⅜'], [1 / 2, '½'], [5 / 8, '⅝'], [2 / 3, '⅔'],
    [3 / 4, '¾'], [5 / 6, '⅚'], [7 / 8, '⅞'], [1, ''],
  ];
  const fraction = fractions.find(([decimal]) => Math.abs(remainder - decimal) < 0.012);
  if (fraction) {
    const integer = whole + (fraction[0] === 1 ? 1 : 0);
    return sign + (fraction[1] ? `${integer ? `${integer} ` : ''}${fraction[1]}` : String(integer));
  }
  return sign + Number(magnitude.toFixed(2)).toString();
}

/** Minimum seasonings retain their baseline amount for smaller batches. */
export function ingredientAmount(ingredient, servings) {
  const amount = Number(ingredient?.amount);
  if (!Number.isFinite(amount)) return NaN;
  const validServings = validateSettings({ servings }).servings;
  if (ingredient.scale === 'fixed') return amount;
  const scaled = amount * validServings / BASE_SERVINGS;
  return ingredient.scale === 'minimum' ? Math.max(amount, scaled) : scaled;
}

/** US measures come from typed source quantities, never a generic g-to-cup ratio. */
export function formatIngredient(ingredient, servings, units = 'metric') {
  const amount = ingredientAmount(ingredient, servings);
  if (!Number.isFinite(amount)) return '—';
  if (amount === 0) return 'to taste';
  const hasUS = (units === 'us' || ingredient.displayMeasure === 'spoon')
    && finite(ingredient?.us?.amount) && ingredient.us.unit;
  const displayAmount = hasUS && ingredient.amount
    ? ingredient.us.amount * amount / ingredient.amount
    : amount;
  let unit = hasUS ? ingredient.us.unit : ingredient.unit;
  let shown = displayAmount;
  if(units==='us'&&!hasUS&&unit==='g'){shown=amount/28.349523125;unit='oz';}
  if(units==='us'&&!hasUS&&unit==='ml'){shown=amount/29.5735295625;unit='fl oz';}
  // Typed source measures can land just below a decimal half after rescaling.
  const roundedOunces = Math.round((shown + Number.EPSILON * Math.abs(shown)) * 10) / 10;
  const quantity=unit==='oz'||unit==='fl oz'?String(roundedOunces):formatQuantity(shown);
  return `${quantity}${unit ? ` ${unit}` : ''}`;
}

/** Safe endpoints round upward; appliance settings round to the nearest 5°C. */
export function temperature(fahrenheit, units = 'us', safety = false) {
  if (!finite(fahrenheit)) return '—';
  const original = `${formatQuantity(fahrenheit)}°F`;
  if (units !== 'metric') return original;
  const celsius = (fahrenheit - 32) * 5 / 9;
  const shown = safety ? Math.ceil(celsius - 1e-10) : Math.round(celsius / 5) * 5;
  return `${shown}°C (${original})`;
}

export function filterRecipes(recipes, filters = {}) {
  const {
    query = '', group = '', appliance = '', maxActive = 0, maxTotal = 0,
    proteinType = '', avoidAllergens = [], booster = '', sort = 'active', maxInterventions = -1, familyDiners = 0, familyChoice = {},
  } = filters;
  const words = clean(query).split(/\s+/).filter(Boolean);
  const avoided = new Set((Array.isArray(avoidAllergens) ? avoidAllergens : []).map(clean));
  return (Array.isArray(recipes) ? recipes : []).filter((recipe) => {
    if (group && recipe.group !== group) return false;
    if (appliance && recipe.appliance !== appliance) return false;
    if (proteinType && (proteinType === 'vegetarian'
      ? recipe.vegetarian !== true
      : recipe.proteinType !== proteinType)) return false;
    if (booster && !(recipe.boosters ?? []).some((item) => clean(item) === clean(booster))) return false;
    if (Number(maxInterventions)>=0 && (!finite(recipe.midCookActions)||recipe.midCookActions>Number(maxInterventions))) return false;
    if (Number(maxActive) > 0 && (!finite(recipe.activeMinutes) || recipe.activeMinutes > Number(maxActive))) return false;
    if (Number(maxTotal) > 0 && (recipe.timeVariable || !finite(recipe.totalMax) || recipe.totalMax > Number(maxTotal))) return false;
    const option = Number(familyDiners)>0 && recipe.group==='shared' ? ((recipe.familyOptions??[]).find(o=>o.id===familyChoice?.[recipe.id]) || recipe.familyOptions?.[0]) : null;
    if ([...(recipe.allergens ?? []),...(option?.allergens??[])].some((allergen) => avoided.has(clean(allergen)))) return false;
    const text = clean([recipe.title, recipe.key, ...(recipe.ingredients ?? []).map((i) => i.name)].join(' '));
    return words.every((word) => text.includes(word));
  }).sort((a, b) => {
    if (sort === 'protein') return (b.nutrition?.protein_g ?? 0) - (a.nutrition?.protein_g ?? 0) || a.title.localeCompare(b.title);
    const key = sort === 'total' ? 'totalMax' : 'activeMinutes';
    return (a[key] ?? Infinity) - (b[key] ?? Infinity) || a.title.localeCompare(b.title);
  });
}


/** Fixed liquid minimums can change nutrition per adult in smaller batches. */
export function servingNutrition(recipe,servings=4){
 const count=validateSettings({servings}).servings;
 const result={...recipe.nutrition};
 for(const ingredient of recipe.ingredients??[]){
  if(!ingredient.nutritionBatch||!ingredient.amount)continue;
  const actual=ingredientAmount(ingredient,count)/ingredient.amount;
  for(const key of NUTRIENTS)result[key]+=(Number(ingredient.nutritionBatch[key]??0)*(actual-count/4))/count;
 }
 return result;
}

/** A family's serving receives one chosen starch; the keto base stays untouched. */
export function familyNutrition(recipe, choiceId, servings=4) {
  const option = recipe?.group === 'shared'
    ? ((recipe.familyOptions ?? []).find((item) => item.id === choiceId) || recipe.familyOptions?.[0])
    : undefined;
  return Object.fromEntries(NUTRIENTS.map((key) => [
    key,
    Number(recipe ? servingNutrition(recipe,servings)[key] : 0) + Number(option?.nutrition?.[key] ?? 0),
  ]));
}

/** Repeated foods combine only when their identity, food state, and measure agree. */
export function shoppingList(recipes, selectedIds, settings = {}) {
  const { servings, familyDiners } = validateSettings(settings);
  const chosen = new Set(Array.isArray(selectedIds) ? selectedIds : []);
  const familyChoice = settings?.familyChoice && typeof settings.familyChoice === 'object'
    ? settings.familyChoice : {};
  const lines = new Map();
  const add = (item, amount, us) => {
    if (!finite(amount) || amount < 0) return;
    const state = item.state ?? '';
    const key = JSON.stringify([item.id, state, item.unit]);
    const current = lines.get(key);
    if (!current) {
      lines.set(key, {
        id: item.id, name: item.name, state, amount, unit: item.unit,
        category: item.category ?? '', note: item.note ?? '', ...(item.displayMeasure?{displayMeasure:item.displayMeasure}:{}), ...(item.package?{package:item.package}:{}),
        ...(us ? { us: { amount: us.amount, unit: us.unit } } : {}),
      });
      return;
    }
    current.amount += amount;
    if (current.displayMeasure !== item.displayMeasure) delete current.displayMeasure;
    if (item.note && !current.note.split(' · ').includes(item.note)) {
      current.note = [current.note, item.note].filter(Boolean).join(' · ');
    }
    if (current.us && us && current.us.unit === us.unit
      && Math.abs(current.us.amount / (current.amount - amount) - us.amount / amount) < 0.0001) {
      current.us.amount += us.amount;
    } else { delete current.us; delete current.displayMeasure; }
  };

  for (const recipe of Array.isArray(recipes) ? recipes : []) {
    if (!chosen.has(recipe.id)) continue;
    for (const ingredient of recipe.ingredients ?? []) {
      const amount = ingredientAmount(ingredient, servings);
      const us = ingredient.us?.amount && ingredient.amount
        ? { amount: ingredient.us.amount * amount / ingredient.amount, unit: ingredient.us.unit }
        : undefined;
      add(ingredient, amount, us);
    }
    if (recipe.group !== 'shared' || familyDiners === 0) continue;
    const options = recipe.familyOptions ?? [];
    const option = options.find((item) => item.id === familyChoice[recipe.id]) ?? options[0];
    if (!option) continue;
    add({
      id: option.ingredientId ?? option.id,
      name: option.ingredientName ?? option.label,
      state: option.state ?? '', unit: option.unit, category: option.category,
      note: option.note,
    }, Number(option.amount) * familyDiners,
    finite(option.us?.amount) && option.us.unit
      ? { amount: option.us.amount * familyDiners, unit: option.us.unit }
      : undefined);
  }
  return [...lines.values()].sort((a, b) => a.category.localeCompare(b.category) || a.name.localeCompare(b.name));
}

export function capacityNote(servings) {
  const count = validateSettings({ servings }).servings;
  if (count > BASE_SERVINGS) return 'More than four servings may need extra pan or basket batches. Keep the stated food thickness and thermometer endpoint; total time can increase.';
  if (count < BASE_SERVINGS) return 'Use the stated cook times as a starting point for this smaller batch. Check the thermometer endpoint; do not shorten a pressure minimum.';
  return 'The listed pan and basket capacity, cook times, and thermometer endpoint are for four servings.';
}

/** Package counts are shopping estimates; recipe weights remain the measured target. */
export function purchaseNote(ingredient,servings=4){
 const pack=ingredient?.package;const amount=ingredientAmount(ingredient,servings);
 if(!pack||!finite(pack.grams)||pack.grams<=0||!finite(amount))return '';
 const count=Math.ceil(amount/pack.grams-1e-10);
 return pack.drained?`About ${count} × ${pack.label}, assuming ~${pack.grams} g drained per can; check actual yield.`:`Buy ${count} × ${pack.label}; measure out the required weight.`;
}
