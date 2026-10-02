# Meal library data contract

All recipe ingredient amounts describe the reviewed four-adult base, except familyOptions which describe one non-keto adult's starch. The 12 recipe IDs preserve the static article anchors. Canonical units distinguish mass, volume, count and spoon measures; source-specific US measures describe the same food quantity. Pesto and pressure liquid stay weighed/measured in grams/mL in both display modes because generic spoon conversions would be misleading.

Linear ingredient scaling supports 2/4/6/8 adults. Pressure liquid has a minimum constraint matching the named Duo 6 QT manual. Its small-batch per-serving nutrient difference is recalculated from the model's all-broth-counted contribution. Higher minima for another cooker are outside the numeric estimate and explicitly noted. Time, safe endpoints, cut size, patty geometry and capacity do not scale linearly. Six/eight servings require capacity checks/batches; the frittata explicitly uses two matching dishes. Fractional turkey eggs are beaten and weighed.

Family controls use one valid option per shared recipe. Missing or invalid option IDs fall back to its first choice consistently in detail, nutrition and groceries. Option allergens enter meal filtering only when non-keto diners are above zero. Known ingredient exclusions are not a cross-contact or brand guarantee. Neither generic feta nor generic Parmesan is certified vegetarian; those recipes are conservatively plant-forward, with label guidance. The harissa/yogurt meal is vegetarian as specified.

Groceries aggregate by ingredient identity + food state + unit. Cut/preparation states remain distinct; checking one cannot check another. Source-specific compatible US measures are summed. If incompatible spoon/cup measures combine, display uses typed mass-to-mass or volume-to-volume fallback, never an invented density. Package guides calculate purchases from scaled net/drained weights; a drained can's ~240 g yield is an approximate planning assumption derived from the source recipe's two-can/480 g convenience estimate. Purchased brands can differ; weigh drained food.

midCookActions counts scheduled starts, shakes, flips and ingredient additions to the main cooking appliances. The filter is explicitly labeled scheduled main-appliance actions; cold-side preparation and family-starch heating remain active work outside this count. Terminal temperature checks and separate food finish checks always remain; optional oven rack swaps are disclosed. It does not mean the appliance may be left unattended. Pressure timeVariable is excluded from a bounded time filter. Above four servings, active/total filters and labels explicitly refer to a batch; extra batches may add time.

Nutrition objects copy the unrounded ingredient model at four servings; presentation rounds estimates. servingNutrition adjusts fixed minimums for smaller batches. Family nutrition adds a measured starch to one base serving, leaving keto servings unchanged. Original recipe formulas, USDA records, label evidence and cooking adaptation boundaries remain in the persistent handoff package at `/Users/johnsolly/Documents/Codex/2026-10-02/overhaul-https-www-blogthedata-com-post/outputs/evidence/`. Recipe source links and modeled limits are also retained in the canonical data and public guide. No cooking, tasting or stopwatch testing is claimed.

Maintain recipes.json and its unit/allergen/family metadata together. Do not make protein-critical yogurt/Parmesan optional without recalculating. Do not substitute frozen/raw/dry food states or sauce brands without reviewing the resulting method and nutrition. The data notes are product assumptions, not a medical nutrition prescription.

Small measured finishing ingredients marked displayMeasure=spoon retain their typed spoon quantity in both metric and US modes. Ingredient model mass is unchanged; it does not require tiny weighing. Consolidation preserves that preference only for compatible allocations.

flow stores the mandatory TRN operation tree: ingredient leaves with fractional allocations (sum1) or a paired symbolic salt pinch/remainder, operations with children, and preparation rows. The renderer validates every ingredient, compacts same-input successive actions, and computes nonoverlapping rowspan/colspan cells. Family starch remains separate from the base tree. Current-setting assistant documents expose the rendered cell graph and measured family options without requiring model-weight precision.

Assistant JSON uses schemaVersion1 and contains current settings, stable recipe IDs, readable quantities, food states, dependency cells, steps, sources, restrictions, estimates and illustration metadata. Static downloads are for4adults, US units, no family starch selected; every shared recipe includes per-person starch options. Downloaded current-setting JSON and copied Markdown use the same recipeDocument as printing.

## Maintenance in this repository

The canonical recipe data is `src/components/recipes/recipes.json`. Run these commands
from `/Users/johnsolly/code/awesome-django-blog` after editing it:

```bash
npm run recipes:sync
npm run test:recipes
npm run gate
```

`recipes:sync` regenerates all twelve complete recipe sections and the three
overview/nutrition/family tables in the existing article. It preserves frontmatter
except the generated excerpt, and preserves editorial guidance. It also updates `public/data/recipe-library.json` and
`public/data/recipe-library.md`. `recipes:check` checks synchronization without
writing files and runs in the app gate. Review editorial advice when the method,
food state, capacity or nutrition changes; generated sections cannot do that.

Keep the `recipe-generated` begin/end comments around generated regions. Recipe
regions use stable recipe IDs; the three comparison tables each have their own
key. Titles and region order can change without changing ownership. Add editorial
content outside these comments; it remains untouched, including HTML tables.

The article retains `/post/15-minute-dump-and-go-instant-pot-recipes/`. Its route
uses `RecipeExperience.astro` with the host-sanitized article as a complete
fallback that stays visible until the interactive library hydrates successfully.
Disabled, blocked or failed JavaScript therefore retains the complete guide.
Only catalog images gain responsive attributes after
sanitization; the twelve TRN regions support keyboard scrolling. Interactive,
print and export views share the same ingredient and dependency model.

During this migration only, an explicit rewrite receipt pins the authorized
replacement and the original legacy record. Reconcile any new frozen-source
changes before updating that receipt. Ordinary publishing after cutover uses the
normal gate and does not require parity with the retired application source.
