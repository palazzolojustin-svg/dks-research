/* X02 dicks.com / golfgalaxy.com catalog census - run in the DevTools console of an open
   https://www.dickssportinggoods.com (or https://www.golfgalaxy.com) tab in a normal browser.
   How to rerun weekly:
     1. Open any dicks.com page in Chrome, F12 -> Console, paste this whole file, Enter.
     2. Run:  await X02run(X02_CATS)            (takes ~10-15 min, polite 1 request at a time)
     3. Run:  copy(X02csv())  -> paste into PB_SCRAPE\raw\X02_dsg_products_<YYYYMMDD>.csv
              copy(JSON.stringify(X02facets)) -> PB_SCRAPE\raw\X02_dsg_brandfacets_<YYYYMMDD>.json
     4. python PB_SCRAPE\scripts\X02_analyze_census.py <csv>
   Data source: each listing page embeds <script id="dcsg-ngx-plp-server-state"> JSON
   (PRODUCT_LIST_API_RESPONSE). Product attribute 6025 = "Vertical Brand" is DKS's own owned-brand flag.
   Sort codes (selectedSort): 0 relevance, 1 Top Sellers, 2 Savings, 5 Featured(default), 6 New Products.
*/
window.X02_CATS = ['womens-athletic-leggings','sports-bras','shop-womens-joggers','womens-shorts-1','womens-jackets-vests',
 'womens-shirts-tops','womens-golf-apparel','mens-shorts','mens-joggers','mens-pants','mens-shirts','mens-golf-apparel',
 'boys-shorts','boys-shirts-tops','girls-shirts-tops','girls-leggings','golf-balls','golf-clubs','putters','golf-drivers',
 'golf-wedges','golf-gloves','golf-bags-accessories-1','dumbbells','weight-benches','yoga-mats','strength-training-equipment',
 'treadmills','camping-coolers','camping-family-tents','sleeping-bags','water-bottles-hydration','backpacks-duffle-bags','bikes',
 'baseball-bats','baseball-gloves','basketballs','all-soccer-balls','mens-running-shoes','womens-running-shoes'];
window.X02rows = window.X02rows || [];
window.X02facets = window.X02facets || {};
window.X02log = window.X02log || [];
window.X02get = async function (path) {
  const res = await fetch(path, {credentials: 'include'});
  const t = await res.text();
  const m = t.match(/id="dcsg-ngx-plp-server-state"[^>]*>([\s\S]*?)<\/script>/);
  if (!m) return {status: res.status, url: res.url, r: null};
  const j = JSON.parse(m[1]);
  return {status: res.status, url: res.url, r: j.PRODUCT_LIST_API_RESPONSE};
};
window.X02parse = function (cat, sort, page, r) {
  const det = r.productDetails || {};
  (r.productVOs || []).forEach((p, i) => {
    let a = [];
    try { a = JSON.parse(p.attributes || '[]'); } catch (e) {}
    const A = {}; a.forEach(o => { for (const k in o) { (A[k.trim()] = A[k.trim()] || []).push(o[k]); } });
    const d = det[p.parentCatentryId] || det[p.catentryId] || {};
    const pr = d.prices || {};
    X02rows.push({
      cat, sort, rank: page * 144 + i + 1, pid: p.parentPartnumber || '', brand: p.mfName || (A.X_BRAND || [''])[0],
      vert: (A['6025'] || []).includes('Vertical Brand') ? 1 : 0, excl: (A['5525'] || [''])[0] || '',
      badge: p.badge || '', d4474: (A['4474'] || [''])[0], sortdate: p.dsgProductSortDate || '',
      minlist: pr.minlistprice || '', minoffer: pr.minofferprice || '', maxlist: pr.maxlistprice || '', maxoffer: pr.maxofferprice || '',
      bvn: (A.X_BazaarVoice_count_DSG || [''])[0], bvr: (A.X_BazaarVoice_ratings_DSG || [''])[0],
      name: (p.name || '').replace(/[",\n]/g, ' ')
    });
  });
};
window.X02run = async function (cats, opts = {}) {
  const maxPages = opts.maxPages || 30, sleep = ms => new Promise(r => setTimeout(r, ms));
  for (const c of cats) {
    try {
      // full listing, default sort
      let x = await X02get(`/f/${c}?pageSize=144&pageNumber=0`);
      if (!x.r) { X02log.push(`${c} FAIL ${x.status}`); continue; }
      const tot = x.r.totalCount;
      X02facets[c] = {total: tot, brands: ((x.r.facetVOs || []).find(f => f.attrIdentifier === 'X_BRAND') || {}).values || {},
        sale: ((x.r.facetVOs || []).find(f => f.attrIdentifier === '5004') || {}).values || {}};
      X02parse(c, 'all', 0, x.r);
      const pages = Math.min(Math.ceil(tot / 144), maxPages);
      for (let p = 1; p < pages; p++) { await sleep(400); x = await X02get(`/f/${c}?pageSize=144&pageNumber=${p}`); if (x.r) X02parse(c, 'all', p, x.r); }
      for (const s of [1, 6]) { await sleep(400); x = await X02get(`/f/${c}?pageSize=144&pageNumber=0&selectedSort=${s}`); if (x.r) X02parse(c, s === 1 ? 'top' : 'new', 0, x.r); }
      X02log.push(`${c} ok total=${tot} pages=${pages}`);
    } catch (e) { X02log.push(`${c} ERR ${e}`); }
  }
  X02log.push('DONE');
};
window.X02csv = function () {
  const k = ['cat','sort','rank','pid','brand','vert','excl','badge','d4474','sortdate','minlist','minoffer','maxlist','maxoffer','bvn','bvr','name'];
  return [k.join(',')].concat(X02rows.map(r => k.map(x => r[x]).join(','))).join('\n');
};
