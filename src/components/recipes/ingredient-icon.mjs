// Decorative Unicode food symbols; names remain the accessible ingredient labels.
const icons = [
  [/\bwater\b/i, '💧'], [/strawberr/i, '🍓'], [/banana/i, '🍌'],
  [/bell pepper/i, '🫑'], [/green beans/i, '🫛'],
  [/cooked rice/i, '🍚'], [/pita|tortilla/i, '🫓'], [/\bbun\b/i, '🍞'],
  [/chickpea|lentil/i, '🫘'], [/parmesan/i, '🧀'],
  [/oregano|basil/i, '🌿'], [/chili|paprika|harissa/i, '🌶️'],
  [/broth/i, '🥣'],
  [/salt/i, '🧂'],
  [/chicken|turkey/i, '🍗'], [/salmon|cod|fish/i, '🐟'], [/egg/i, '🥚'],
  [/olive oil/i, '🫒'], [/broccoli/i, '🥦'], [/cabbage|spinach|lettuce|salad greens/i, '🥬'],
  [/cucumber/i, '🥒'], [/potato/i, '🥔'], [/tomato/i, '🍅'], [/lemon|lime/i, '🍋'],
  [/garlic/i, '🧄'], [/onion/i, '🧅'], [/avocado/i, '🥑'], [/beans/i, '🫘'],
  [/feta|cheese/i, '🧀'],
];
export function ingredientIcon(name) {
  return icons.find(([pattern]) => pattern.test(name))?.[1] || '';
}
