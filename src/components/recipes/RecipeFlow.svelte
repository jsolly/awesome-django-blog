<script>
 import {flowHtml} from './trn-logic.mjs';
 let {recipe,settings}=$props();
 const html=$derived(flowHtml(recipe,settings));
</script>
<section class="trn-view" aria-label="Tabular recipe notation"><h3>Cooking flow</h3><p class="trn-help">Read left to right. Each merged cell acts on the ingredient rows feeding into it. Parallel branches stay separate until plating. Amounts below use your servings and units; scroll the table sideways on a small screen.</p>{@html html}</section>
<style>
 .trn-view{margin:26px 0;max-width:100%;min-width:0}.trn-help{font-size:.85rem;line-height:1.5;max-width:55rem}
 .trn-view :global(.trn-scroll){overflow-x:auto;max-width:100%;border:1px solid #3b7046;border-radius:6px}
 .trn-view :global(.trn-scroll:focus-visible){outline:3px solid #3b7046;outline-offset:3px}
 .trn-view :global(.trn-table){border-collapse:collapse;width:100%;min-width:760px;table-layout:auto;margin:0!important;font-size:14px;line-height:1.4;background:#fffdf5;color:#241c14}
 .trn-view :global(caption){text-align:left;padding:10px;font-size:13px;background:#eff3e5;color:#241c14}
 .trn-view :global(th),.trn-view :global(td){border:1px solid #3b7046;padding:8px;vertical-align:middle;white-space:normal;overflow-wrap:anywhere}
 .trn-view :global(.trn-ingredient){font-weight:400;text-align:left;min-width:220px}
 .trn-view :global(.trn-ingredient small){display:block;font-size:11px;line-height:1.3;margin-top:3px}
 .trn-view :global(.trn-operation){text-align:center;min-width:100px;max-width:200px}
 .trn-view :global(.trn-prep){text-align:center;background:#f0f4e9}
 @media print{
 .trn-view{margin:10pt 0;break-inside:avoid}.trn-help{display:none}.trn-view h3{font:700 12pt/1.2 Georgia,serif;margin:6pt 0}
 .trn-view :global(.trn-scroll){overflow:visible;border:0;border-radius:0}
 .trn-view :global(.trn-table){min-width:0!important;width:100%;table-layout:fixed;font-size:8pt!important;line-height:1.2!important;background:white!important}
 .trn-view :global(th),.trn-view :global(td){padding:3pt!important;min-width:0!important;max-width:none!important;line-height:1.2!important;font-size:8pt!important;border-color:#555!important}
 .trn-view :global(.trn-ingredient small){font-size:7pt!important}
 .trn-view :global(caption){font-size:8pt!important;padding:4pt!important}
 }
</style>
