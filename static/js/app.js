/* Chiang Mai community guide — single-page app over static/data.json */
(() => {
  'use strict';

  // ---------- Constants ----------
  const CATS = {
    cafe_restaurant: { label: 'Еда и кофе', icon: '☕', color: '#d97706' },
    wellness:        { label: 'Спа и здоровье', icon: '💆', color: '#db2777' },
    services:        { label: 'Сервисы и клиники', icon: '🏥', color: '#2563eb' },
    stay:            { label: 'Жильё', icon: '🏨', color: '#7c3aed' },
    workspace:       { label: 'Коворкинги', icon: '💻', color: '#0891b2' },
    nature:          { label: 'Природа', icon: '🌿', color: '#16a34a' },
    hiking_trail:    { label: 'Тропы', icon: '🥾', color: '#65a30d' },
    event:           { label: 'Событие', icon: '📅', color: '#dc2626' },
  };
  const CAT_ORDER = ['cafe_restaurant', 'nature', 'wellness', 'services', 'workspace', 'stay'];
  const CAT_GROUP = { nature: ['nature', 'hiking_trail'] };
  const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const DAYS_RU = { Mon: 'пн', Tue: 'вт', Wed: 'ср', Thu: 'чт', Fri: 'пт', Sat: 'сб', Sun: 'вс' };
  const MONTHS_RU = ['янв', 'фев', 'мар', 'апр', 'мая', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'];
  const PAGE = 36;
  const CM_CENTER = [18.7883, 98.9853];
  const SYNONYMS = [
    ['кофе', 'coffee', 'кофейня', 'roaster', 'espresso'], ['веган', 'vegan', 'вегетариан', 'plant'],
    ['стоматолог', 'dental', 'зубн', 'dentist'], ['массаж', 'massage', 'спа', 'spa'],
    ['водопад', 'waterfall'], ['озеро', 'lake', 'reservoir', 'водохранилище'], ['храм', 'wat', 'temple'],
    ['коворкинг', 'coworking', 'cowork'], ['сауна', 'sauna', 'ice bath', 'баня'], ['йога', 'yoga'],
    ['бассейн', 'pool'], ['зал', 'gym', 'fitness', 'фитнес'], ['бургер', 'burger'], ['пицца', 'pizza'],
    ['суши', 'sushi', 'japanese', 'япон'], ['завтрак', 'breakfast', 'brunch', 'бранч'],
    ['ветеринар', 'vet', 'animal', 'pet', 'ветклиника'], ['дети', 'kids', 'детск', 'family', 'children'],
    ['байк', 'bike', 'scooter', 'скутер', 'rental', 'прокат', 'аренда'], ['клиника', 'clinic', 'hospital', 'госпиталь', 'больница'],
    ['рынок', 'market', 'маркет', 'базар'], ['бар', 'bar', 'пиво', 'beer', 'craft', 'крафт'],
    ['отель', 'hotel', 'resort', 'резорт', 'кондо', 'condo'], ['парк', 'park'], ['кемпинг', 'camping', 'glamping', 'глэмпинг'],
    ['горячие источники', 'hot spring', 'источник'], ['музыка', 'jazz', 'джаз', 'live', 'концерт'],
  ];

  const AREA_ALIASES = { 'Night Bazaar / Chang Khlan': 'Night Bazaar', 'San Kamphaeng / Doi Saket': 'Doi Saket / San Kamphaeng', 'Mae Taeng / Chiang Dao': 'Chiang Dao / Mae Taeng' };

  // ---------- State ----------
  const S = {
    data: null, items: [], byId: new Map(), reviews: null, wiki: [],
    view: 'places', cat: 'all', area: '', q: '', veg: false, sort: 'popular',
    eventsMode: 'upcoming', page: 1,
    me: null, // {lat, lng}
    map: null, cluster: null, meMarker: null, markers: new Map(),
    detailId: null, detailMap: null, routeMap: null,
  };
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const todayISO = () => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`; };

  // ---------- Helpers ----------
  function photoOf(item) {
    const p = item.photos && item.photos[0];
    return p ? p.replace(/^\//, '') : null;
  }
  function imgOrPh(item, cls = '') {
    const p = photoOf(item);
    const ico = (CATS[item.category] || {}).icon || '📍';
    return p
      ? `<img src="${esc(p)}" alt="" loading="lazy" onerror="this.replaceWith(Object.assign(document.createElement('div'),{className:'ph',textContent:'${ico}'}))" class="${cls}">`
      : `<div class="ph ${cls}">${ico}</div>`;
  }
  function km(a, b) {
    if (!a || !b) return null;
    const R = 6371, dLat = (b.lat - a.lat) * Math.PI / 180, dLng = (b.lng - a.lng) * Math.PI / 180;
    const x = Math.sin(dLat / 2) ** 2 + Math.cos(a.lat * Math.PI / 180) * Math.cos(b.lat * Math.PI / 180) * Math.sin(dLng / 2) ** 2;
    return R * 2 * Math.atan2(Math.sqrt(x), Math.sqrt(1 - x));
  }
  const fmtKm = (d) => d == null ? '' : d < 1 ? `${Math.round(d * 1000)} м` : d < 10 ? `${d.toFixed(1)} км` : `${Math.round(d)} км`;
  const hasGeo = (i) => i.latitude && i.longitude;
  const geoOf = (i) => hasGeo(i) ? { lat: i.latitude, lng: i.longitude } : null;
  const areaLabel = (a) => AREA_ALIASES[a] || a;
  function distOf(item) { return S.me ? km(S.me, geoOf(item)) : null; }

  function hoursToday(item) {
    const h = item.opening_hours;
    if (!h || typeof h !== 'object') return null;
    const d = DAYS[new Date().getDay()];
    return h[d] ? { day: d, text: h[d] } : null;
  }
  function priceHint(item) {
    const p = item.community_summary && item.community_summary.pricing;
    if (!p || !p.length) return null;
    // first price-looking token that reads like a typical spend, not a procedure price (implants, courses)
    for (const m of p.join(' ').matchAll(/(\d[\d\s,.–-]*\d|\d)\s*(THB|бат|฿|baht)/gi)) {
      const first = parseInt(m[1].replace(/[\s,.]/g, '').split(/[–-]/)[0], 10);
      if (first > 0 && first <= 5000) return `${m[1].replace(/\s+/g, '')} ฿`;
    }
    return null;
  }
  function highlight(item) {
    const cs = item.community_summary;
    if (cs && cs.highlights && cs.highlights.length) return cs.highlights[0];
    return (item.description || '').split(/(?<=[.!?])\s/)[0];
  }
  function normalize(s) { return (s || '').toLowerCase().replace(/ё/g, 'е'); }
  function expandQuery(q) {
    const terms = new Set([q]);
    for (const group of SYNONYMS) if (group.some((g) => q.includes(g) || g.includes(q))) group.forEach((g) => terms.add(g));
    return [...terms];
  }
  function matches(item, q) {
    if (!q) return true;
    const terms = expandQuery(normalize(q));
    const hay = normalize([item.title, item.description, item.neighborhood, item.venue_name, item.address, item.google_category,
      ...(item.community_summary ? [].concat(item.community_summary.highlights || [], item.community_summary.tips || [], item.community_summary.pricing || []) : [])].join(' '));
    // synonyms must start a word ("wat" must not match "waterfall"); the raw query may match anywhere
    const nq = normalize(q);
    if (hay.includes(nq)) return true;
    return terms.some((t) => t !== nq && t.length > 1 && new RegExp('(^|[^a-zа-я0-9])' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).test(hay));
  }
  function toast(msg) {
    const t = $('toast'); t.textContent = msg; t.hidden = false;
    clearTimeout(toast._t); toast._t = setTimeout(() => (t.hidden = true), 2200);
  }
  function share(title, url) {
    if (navigator.share) navigator.share({ title, url }).catch(() => {});
    else navigator.clipboard.writeText(url).then(() => toast('Ссылка скопирована'));
  }
  function mapsUrl(item) {
    if (item.location_url) return item.location_url;
    if (hasGeo(item)) return `https://www.google.com/maps/search/?api=1&query=${item.latitude},${item.longitude}`;
    return null;
  }

  // ---------- Router ----------
  function parseHash() {
    const h = location.hash.replace(/^#\/?/, '');
    const [pathPart, queryPart] = h.split('?');
    const path = pathPart.split('/').filter(Boolean);
    const params = new URLSearchParams(queryPart || '');
    return { path, params };
  }
  function buildHash(view, params = {}, sub = '') {
    const p = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) if (v) p.set(k, v);
    const qs = p.toString();
    const base = view === 'places' ? '' : view;
    return `#/${base}${sub ? (base ? '/' : '') + sub : ''}${qs ? '?' + qs : ''}`;
  }
  function placesHash() { return buildHash('places', { cat: S.cat !== 'all' ? S.cat : '', area: S.area, q: S.q, veg: S.veg ? '1' : '', sort: S.sort !== 'popular' ? S.sort : '' }); }
  function syncUrl() { if (S.view === 'places' || S.view === 'map') history.replaceState(null, '', S.view === 'map' ? buildHash('map', { cat: S.cat !== 'all' ? S.cat : '', q: S.q }) : placesHash()); }

  function route() {
    const { path, params } = parseHash();
    const view = path[0] || 'places';
    // place detail can sit on top of any view: #/place/123
    if (view === 'place') {
      if (!document.querySelector('.view.active')) { showView('places'); syncControls(); renderPlaces(); } // cold load of a shared link
      openDetail(+path[1]); return;
    }
    closeDetail(false);

    if (view === 'places' || view === '') {
      S.cat = params.get('cat') || 'all'; S.area = params.get('area') || ''; S.q = params.get('q') || '';
      S.veg = params.get('veg') === '1'; S.sort = params.get('sort') || 'popular'; S.page = 1;
      showView('places'); syncControls(); renderPlaces();
    } else if (view === 'map') {
      S.cat = params.get('cat') || S.cat; S.q = params.get('q') || S.q;
      showView('map'); syncControls(); renderMap();
    } else if (view === 'events') {
      showView('events'); renderEvents();
    } else if (view === 'routes') {
      showView('routes'); path[1] ? renderRoute(+path[1]) : renderRoutesIndex();
    } else if (view === 'wiki') {
      showView('wiki'); path[1] ? renderWikiArticle(path[1]) : renderWikiIndex();
    } else { location.hash = '#/'; }
  }
  function showView(v) {
    S.view = v;
    document.querySelectorAll('.view').forEach((el) => el.classList.toggle('active', el.id === 'view-' + v));
    document.querySelectorAll('[data-view]').forEach((a) => a.classList.toggle('active', a.dataset.view === v));
    if (v !== 'map') window.scrollTo({ top: 0 });
    $('searchInput').placeholder = v === 'wiki' ? 'Поиск по справочнику…' : v === 'events' ? 'Поиск по афише…' : 'Кофе, стоматолог, водопад, Нимман…';
  }
  function syncControls() {
    $('searchInput').value = S.q; $('searchClear').hidden = !S.q;
    $('areaSelect').value = S.area; $('vegToggle').checked = S.veg; $('sortSelect').value = S.sort;
    $('vegToggleWrap').hidden = !(S.cat === 'all' || S.cat === 'cafe_restaurant');
    renderChips('catChips'); renderChips('mapCatChips'); renderChips('mapCatChipsMobile');
    $('nearBtn').classList.toggle('on', !!S.me); $('mapNearBtn').classList.toggle('on', !!S.me);
  }

  // ---------- Filtering ----------
  function placeItems() { return S.items.filter((i) => i.category !== 'event'); }
  function filtered() {
    let list = placeItems().filter((i) => {
      if (S.cat !== 'all') { const g = CAT_GROUP[S.cat] || [S.cat]; if (!g.includes(i.category)) return false; }
      if (S.area && i.neighborhood !== S.area) return false;
      if (S.veg && i.category === 'cafe_restaurant' && !i.veg_friendly) return false;
      return matches(i, S.q);
    });
    const sort = S.sort === 'distance' && !S.me ? 'popular' : S.sort;
    if (sort === 'rating') list.sort((a, b) => (b.rating || 0) - (a.rating || 0) || (b.rating_count || 0) - (a.rating_count || 0));
    else if (sort === 'newest') list.sort((a, b) => (b.updated_at || '').localeCompare(a.updated_at || ''));
    else if (sort === 'alpha') list.sort((a, b) => a.title.localeCompare(b.title, 'ru'));
    else if (sort === 'distance') list.sort((a, b) => (distOf(a) ?? 1e9) - (distOf(b) ?? 1e9));
    else list.sort((a, b) => (b.mention_count || 0) - (a.mention_count || 0) || (b.rating_count || 0) - (a.rating_count || 0));
    return list;
  }

  // ---------- Chips ----------
  function renderChips(containerId) {
    const el = $(containerId); if (!el) return;
    const counts = {};
    for (const i of placeItems()) { counts[i.category] = (counts[i.category] || 0) + 1; }
    const total = placeItems().length;
    const chip = (key, label, n) => `<button class="chip ${S.cat === key ? 'active' : ''}" data-cat="${key}">${label}<span class="n">${n}</span></button>`;
    el.innerHTML = chip('all', 'Все', total) + CAT_ORDER.map((c) => {
      const g = CAT_GROUP[c] || [c];
      return chip(c, `${CATS[c].icon} ${CATS[c].label}`, g.reduce((s, k) => s + (counts[k] || 0), 0));
    }).join('');
    el.querySelectorAll('.chip').forEach((b) => b.addEventListener('click', () => { S.cat = b.dataset.cat; S.page = 1; syncControls(); syncUrl(); S.view === 'map' ? renderMap() : renderPlaces(); }));
  }

  // ---------- Cards ----------
  function cardHtml(item) {
    const c = CATS[item.category] || {};
    const d = distOf(item);
    const price = priceHint(item);
    const ht = hoursToday(item);
    return `<article class="card" data-id="${item.id}">
      <div class="card-img">${imgOrPh(item)}
        <div class="card-badges"><span class="badge">${c.icon || ''} ${esc(c.label || '')}</span>${d != null ? `<span class="badge dist">${fmtKm(d)}</span>` : ''}</div>
      </div>
      <div class="card-body">
        <div class="card-title">${esc(item.title)}</div>
        <div class="card-meta">${item.neighborhood && item.neighborhood !== 'Other' ? `<span>${esc(areaLabel(item.neighborhood))}</span>` : ''}${ht ? `<span class="dot"></span><span>${esc(ht.text)}</span>` : ''}</div>
        <div class="card-text">${esc(highlight(item))}</div>
        <div class="card-foot">
          ${item.rating ? `<span class="pill rating">★ ${item.rating}</span>` : ''}
          ${price ? `<span class="pill">${esc(price)}</span>` : ''}
          ${item.veg_friendly ? '<span class="pill veg">🌱 veg</span>' : ''}
          <span style="margin-left:auto">💬 ${item.mention_count || 1}</span>
        </div>
      </div>
    </article>`;
  }
  function bindCards(root) {
    root.querySelectorAll('[data-id]').forEach((el) => el.addEventListener('click', (e) => { if (e.target.closest('a')) return; openDetail(+el.dataset.id, true); }));
  }

  function renderPlaces() {
    const list = filtered();
    const grid = $('placesGrid');
    $('placesCount').textContent = list.length ? `${list.length} ${plural(list.length, 'место', 'места', 'мест')}` : '';
    const slice = list.slice(0, PAGE * S.page);
    grid.innerHTML = slice.length ? slice.map(cardHtml).join('') : `<div class="empty"><b>Ничего не нашлось</b>Попробуйте другой запрос или снимите фильтры</div>`;
    bindCards(grid);
    $('placesMore').hidden = list.length <= slice.length;
    // wiki hits for search
    const wh = $('wikiHits');
    if (S.q && S.wiki.length) {
      const hits = S.wiki.filter((a) => matches({ title: a.title, description: a.content }, S.q)).slice(0, 4);
      wh.innerHTML = hits.map((a) => `<a href="#/wiki/${a.id}">📖 <span>${esc(a.title)}</span></a>`).join('');
      wh.hidden = !hits.length;
    } else wh.hidden = true;
  }
  function plural(n, a, b, c) { const m = n % 10, h = n % 100; return (m === 1 && h !== 11) ? a : (m >= 2 && m <= 4 && (h < 10 || h >= 20)) ? b : c; }

  // ---------- Geolocation ----------
  function locate(cb) {
    if (!navigator.geolocation) return toast('Геолокация недоступна');
    toast('Определяю местоположение…');
    navigator.geolocation.getCurrentPosition((p) => {
      S.me = { lat: p.coords.latitude, lng: p.coords.longitude };
      if (km(S.me, { lat: CM_CENTER[0], lng: CM_CENTER[1] }) > 300) toast('Похоже, вы не в Чиангмае — покажу расстояния до города');
      S.sort = 'distance'; syncControls(); syncUrl();
      cb && cb();
    }, () => toast('Не удалось получить местоположение'), { enableHighAccuracy: false, timeout: 8000, maximumAge: 300000 });
  }

  // ---------- Map ----------
  function tiles() {
    return L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>', maxZoom: 19,
    });
  }
  function pinIcon(item) {
    const c = CATS[item.category] || {};
    return L.divIcon({ className: '', html: `<div class="pin" style="background:${c.color || '#888'}"><span>${c.icon || '📍'}</span></div>`, iconSize: [28, 28], iconAnchor: [14, 28], popupAnchor: [0, -26] });
  }
  function ensureMap() {
    if (S.map) return;
    S.map = L.map('map', { zoomControl: true, attributionControl: true }).setView(CM_CENTER, 12);
    tiles().addTo(S.map);
    S.cluster = L.markerClusterGroup({ maxClusterRadius: 44, showCoverageOnHover: false, disableClusteringAtZoom: 16 });
    S.map.addLayer(S.cluster);
    S.map.on('moveend', updateMapList);
  }
  function renderMap() {
    ensureMap();
    const list = filtered().filter(hasGeo);
    S.cluster.clearLayers(); S.markers.clear();
    for (const item of list) {
      const m = L.marker([item.latitude, item.longitude], { icon: pinIcon(item), title: item.title });
      m.bindPopup(() => popupHtml(item), { closeButton: false });
      m.on('popupopen', (e) => { const el = e.popup.getElement().querySelector('.pop'); el && el.addEventListener('click', () => openDetail(item.id, true)); highlightRow(item.id); });
      S.markers.set(item.id, m); S.cluster.addLayer(m);
    }
    if (S.me) {
      if (S.meMarker) S.meMarker.remove();
      S.meMarker = L.marker([S.me.lat, S.me.lng], { icon: L.divIcon({ className: '', html: '<div class="me-dot"></div>', iconSize: [16, 16], iconAnchor: [8, 8] }), interactive: false }).addTo(S.map);
    }
    $('mapCount').textContent = `${list.length} на карте`;
    // the container was display:none a moment ago — let Leaflet measure it before fitting
    setTimeout(() => { S.map.invalidateSize(); fitOnce(list); updateMapList(); }, 60);
  }
  function fitOnce(list) {
    // fit to the Chiang Mai region only; far-away outliers (Pai, Chiang Rai, Laos) stay reachable by zooming out.
    // Skipped while the container has no size (hidden tab) and retried on the next resize.
    if (renderMap._fitted || !list.length) return;
    if (S.map.getSize().y === 0) { S.map.once('resize', () => fitOnce(list)); return; }
    const near = list.filter((i) => km(geoOf(i), { lat: CM_CENTER[0], lng: CM_CENTER[1] }) < 40);
    S.map.fitBounds(L.latLngBounds((near.length ? near : list).map((i) => [i.latitude, i.longitude])).pad(0.05), { maxZoom: 13 });
    renderMap._fitted = true;
  }
  function popupHtml(item) {
    const p = photoOf(item); const c = CATS[item.category] || {};
    return `<div class="pop">${p ? `<img src="${esc(p)}" alt="">` : ''}<div><b>${esc(item.title)}</b><span>${c.icon || ''} ${esc(c.label || '')}${item.rating ? ` · ★ ${item.rating}` : ''}${distOf(item) != null ? ` · ${fmtKm(distOf(item))}` : ''}</span></div></div>`;
  }
  function updateMapList() {
    if (S.view !== 'map' || !S.map) return;
    const b = S.map.getBounds();
    const visible = filtered().filter((i) => hasGeo(i) && b.contains([i.latitude, i.longitude])).slice(0, 80);
    const row = (i) => `<div class="map-row" data-id="${i.id}">${imgOrPh(i)}<div><b>${esc(i.title)}</b><span>${esc((CATS[i.category] || {}).label || '')}${i.neighborhood && i.neighborhood !== 'Other' ? ' · ' + esc(areaLabel(i.neighborhood)) : ''}${distOf(i) != null ? ' · ' + fmtKm(distOf(i)) : ''}</span></div></div>`;
    const ml = $('mapList');
    ml.innerHTML = visible.length ? visible.map(row).join('') : '<div class="empty">В этой области нет мест</div>';
    ml.querySelectorAll('.map-row').forEach((r) => {
      r.addEventListener('mouseenter', () => { const m = S.markers.get(+r.dataset.id); m && m.setZIndexOffset(1000); });
      r.addEventListener('click', () => focusMarker(+r.dataset.id));
    });
    const strip = $('mapStrip');
    strip.innerHTML = visible.slice(0, 30).map((i) => `<div class="strip-card" data-id="${i.id}">${imgOrPh(i)}<div><b>${esc(i.title)}</b><span>${esc((CATS[i.category] || {}).label || '')}${distOf(i) != null ? ' · ' + fmtKm(distOf(i)) : ''}</span></div></div>`).join('');
    strip.querySelectorAll('.strip-card').forEach((r) => r.addEventListener('click', () => openDetail(+r.dataset.id, true)));
  }
  function focusMarker(id) {
    const m = S.markers.get(id); if (!m) return;
    S.cluster.zoomToShowLayer(m, () => m.openPopup());
  }
  function highlightRow(id) {
    document.querySelectorAll('.map-row').forEach((r) => r.classList.toggle('hl', +r.dataset.id === id));
    const r = document.querySelector(`.map-row[data-id="${id}"]`); r && r.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }

  // ---------- Detail ----------
  async function openDetail(id, push) {
    const item = S.byId.get(id); if (!item) return;
    S.detailId = id; S.detailPushed = !!push;
    if (push) history.pushState(null, '', `#/place/${id}`);
    const c = CATS[item.category] || {};
    const cs = item.community_summary || {};
    const d = distOf(item);
    const ht = hoursToday(item);
    const isEvent = item.category === 'event';
    const maps = mapsUrl(item);
    const list = (arr) => `<ul>${arr.map((x) => `<li>${esc(x)}</li>`).join('')}</ul>`;
    const nearby = !isEvent && hasGeo(item) ? placeItems().filter((i) => i.id !== item.id && hasGeo(i)).map((i) => ({ i, d: km(geoOf(item), geoOf(i)) })).filter((x) => x.d < 3).sort((a, b) => a.d - b.d).slice(0, 5) : [];
    const related = S.wiki.filter((a) => (a.related || []).includes(item.id));

    $('detailPanel').innerHTML = `
      <button class="d-close" id="dClose" aria-label="Закрыть">✕</button>
      <div class="d-hero">${imgOrPh(item)}</div>
      <div class="d-body">
        <div class="d-cat"><span class="cat">${c.icon || ''} ${esc(c.label || '')}</span>${item.neighborhood && item.neighborhood !== 'Other' ? `<span>·</span><span>${esc(areaLabel(item.neighborhood))}</span>` : ''}${item.google_category ? `<span>·</span><span>${esc(item.google_category)}</span>` : ''}</div>
        <h2 class="d-title">${esc(item.title)}</h2>
        <div class="d-facts">
          ${item.rating ? `<span><b>★ ${item.rating}</b> · ${(item.rating_count || 0).toLocaleString('ru')} отзывов</span>` : ''}
          ${d != null ? `<span>📍 <b>${fmtKm(d)}</b> от вас</span>` : ''}
          ${ht ? `<span>🕐 <b>${esc(ht.text)}</b> сегодня</span>` : ''}
          ${isEvent && item.event_date ? `<span>📅 <b>${esc(item.event_date)}</b></span>` : ''}
          ${isEvent && item.venue_name ? `<span>📍 ${esc(item.venue_name)}</span>` : ''}
          <span>💬 ${item.mention_count || 1} ${plural(item.mention_count || 1, 'упоминание', 'упоминания', 'упоминаний')} в чате</span>
        </div>
        <div class="d-actions">
          ${isEvent && item.registration_url ? `<a class="btn btn-primary" href="${esc(item.registration_url)}" target="_blank" rel="noopener">${esc(item.registration_label || 'Записаться')}</a>` : ''}
          ${maps ? `<a class="btn ${isEvent && item.registration_url ? '' : 'btn-primary'}" href="${esc(maps)}" target="_blank" rel="noopener">🧭 Маршрут в Google Maps</a>` : ''}
          ${item.phone_contact ? `<a class="btn" href="tel:${esc(item.phone_contact.replace(/\s/g, ''))}">📞 ${esc(item.phone_contact)}</a>` : ''}
          ${item.website ? `<a class="btn" href="${esc(item.website)}" target="_blank" rel="noopener">🌐 Сайт</a>` : ''}
          <button class="btn" id="dShare" type="button">↗ Поделиться</button>
        </div>
        ${cs.highlights && cs.highlights.length ? `<div class="d-section"><h3>Что говорят в чате</h3>${list(cs.highlights)}</div>` : ''}
        ${cs.pricing && cs.pricing.length ? `<div class="d-section"><h3>Цены</h3>${list(cs.pricing)}</div>` : ''}
        ${cs.tips && cs.tips.length ? `<div class="d-section"><h3>Советы</h3>${list(cs.tips)}</div>` : ''}
        ${item.description ? `<div class="d-section"><h3>Описание</h3><p>${esc(item.description)}</p></div>` : ''}
        ${hasGeo(item) ? `<div class="d-map" id="dMap"></div>` : ''}
        ${item.address ? `<div class="d-section"><h3>Адрес</h3><p>${esc(item.address)}</p></div>` : ''}
        ${item.opening_hours && typeof item.opening_hours === 'object' ? `<div class="d-section"><details class="d-details"><summary>Часы работы</summary><div class="hours">${Object.entries(item.opening_hours).map(([k, v]) => `<span class="${ht && ht.day === k ? 'today' : ''}">${DAYS_RU[k] || k}</span><span class="${ht && ht.day === k ? 'today' : ''}">${esc(v)}</span>`).join('')}</div></details></div>` : ''}
        ${related.length ? `<div class="d-section"><h3>В справочнике</h3><div class="wiki-hits">${related.map((a) => `<a href="#/wiki/${a.id}">📖 <span>${esc(a.title)}</span></a>`).join('')}</div></div>` : ''}
        ${nearby.length ? `<div class="d-section"><h3>Рядом</h3><div class="nearby">${nearby.map(({ i, d }) => `<a href="#/place/${i.id}">${imgOrPh(i)}<div><b>${esc(i.title)}</b><span>${esc((CATS[i.category] || {}).label || '')}</span></div><span>${fmtKm(d)}</span></a>`).join('')}</div></div>` : ''}
        <div class="d-section"><details class="d-details" id="dReviews"><summary>Сообщения из чата (${item.review_count || 0})</summary><div id="dReviewsBody"><div class="empty">Загрузка…</div></div></details></div>
      </div>`;
    $('detail').hidden = false;
    document.body.style.overflow = 'hidden';
    $('dClose').onclick = () => closeDetail(true);
    $('dShare').onclick = () => share(item.title, location.origin + location.pathname + `#/place/${id}`);
    $('detailPanel').scrollTop = 0;

    if (hasGeo(item)) {
      if (S.detailMap) { S.detailMap.remove(); S.detailMap = null; }
      S.detailMap = L.map('dMap', { zoomControl: false, attributionControl: false, dragging: false, scrollWheelZoom: false, touchZoom: false, doubleClickZoom: false }).setView([item.latitude, item.longitude], 15);
      tiles().addTo(S.detailMap);
      L.marker([item.latitude, item.longitude], { icon: pinIcon(item) }).addTo(S.detailMap);
      $('dMap').style.cursor = 'pointer'; $('dMap').onclick = () => { closeDetail(false); location.hash = buildHash('map', {}); setTimeout(() => { S.map.setView([item.latitude, item.longitude], 16); focusMarker(item.id); }, 120); };
    }
    $('dReviews').addEventListener('toggle', async (e) => { if (e.target.open) renderReviews(item); }, { once: true });
  }
  async function renderReviews(item) {
    if (!S.reviews) {
      try { S.reviews = await (await fetch('static/reviews.json')).json(); } catch { S.reviews = {}; }
    }
    const rs = S.reviews[item.id] || [];
    $('dReviewsBody').innerHTML = rs.length ? rs.map((r) => `<div class="review"><div class="review-head"><b>${esc(r.sender_name || 'Аноним')}</b><span>${esc((r.msg_date || '').slice(0, 10))}</span></div><p>${esc(r.review_text)}</p>${r.source_link ? `<a href="${esc(r.source_link)}" target="_blank" rel="noopener">Открыть в Telegram ↗</a>` : ''}</div>`).join('') : '<div class="empty">Пока нет сообщений</div>';
  }
  function closeDetail(pop) {
    if ($('detail').hidden) return;
    $('detail').hidden = true; document.body.style.overflow = '';
    if (S.detailMap) { S.detailMap.remove(); S.detailMap = null; }
    S.detailId = null;
    if (pop && location.hash.startsWith('#/place/')) {
      if (S.detailPushed) history.back();
      else history.replaceState(null, '', '#/'); // opened from a shared link: nothing to go back to
    }
  }

  // ---------- Events ----------
  function renderEvents() {
    const today = todayISO();
    const all = S.items.filter((i) => i.category === 'event' && matches(i, S.q));
    const upcoming = all.filter((i) => !i.event_iso_date || i.event_iso_date >= today).sort((a, b) => (a.event_iso_date || '9999').localeCompare(b.event_iso_date || '9999'));
    const past = all.filter((i) => i.event_iso_date && i.event_iso_date < today).sort((a, b) => b.event_iso_date.localeCompare(a.event_iso_date));
    const list = S.eventsMode === 'upcoming' ? upcoming : past;
    $('eventSeg').querySelectorAll('button').forEach((b) => { b.classList.toggle('active', b.dataset.mode === S.eventsMode); b.textContent = b.dataset.mode === 'upcoming' ? `Предстоящие (${upcoming.length})` : `Прошедшие (${past.length})`; });
    const el = $('eventsList');
    if (!list.length) { el.innerHTML = `<div class="empty"><b>${S.eventsMode === 'upcoming' ? 'Пока нет анонсов' : 'Архив пуст'}</b>Новые события появляются по мере обсуждения в чатах</div>`; return; }
    let lastMonth = '';
    el.innerHTML = list.map((i) => {
      const dt = i.event_iso_date ? new Date(i.event_iso_date + 'T00:00:00') : null;
      const monthKey = dt ? `${MONTHS_RU[dt.getMonth()]} ${dt.getFullYear()}` : 'Без даты';
      const head = monthKey !== lastMonth ? `<div class="event-day">${monthKey}</div>` : '';
      lastMonth = monthKey;
      const p = photoOf(i);
      return head + `<div class="event ${S.eventsMode === 'past' ? 'past' : ''}" data-id="${i.id}">
        <div class="event-date">${dt ? `<b>${dt.getDate()}</b><span>${MONTHS_RU[dt.getMonth()]}</span>` : '<b>—</b>'}</div>
        <div><div class="event-title">${esc(i.title)}</div><div class="event-meta">${[i.event_date, i.venue_name, i.neighborhood !== 'Other' ? areaLabel(i.neighborhood) : ''].filter(Boolean).map(esc).join(' · ')}</div></div>
        ${p ? `<img class="event-thumb" src="${esc(p)}" alt="" loading="lazy">` : '<span></span>'}
      </div>`;
    }).join('');
    bindCards(el);
  }

  // ---------- Routes ----------
  function collectionItems(col) { return (col.items || []).map((x) => ({ ...S.byId.get(x.id), note: x.note })).filter((x) => x.id); }
  function routeCardHtml(c) {
    const items = collectionItems(c);
    const cover = c.cover_image || (items.map(photoOf).find(Boolean));
    return `<article class="card route-card" data-route="${c.id}">
      <div class="card-img">${cover ? `<img src="${esc(cover.replace(/^\//, ''))}" alt="" loading="lazy">` : '<div class="ph">🧭</div>'}<h3>${esc(c.title)}</h3></div>
      <div class="card-body"><div class="card-text">${esc(c.description || '')}</div>
      <div class="card-foot route-stats">${c.duration ? `<span>⏱ ${esc(c.duration)}</span>` : ''}${c.transport ? `<span>🛵 ${esc(c.transport)}</span>` : ''}${c.budget ? `<span>💸 ${esc(c.budget)}</span>` : ''}<span>${items.length} ${plural(items.length, 'место', 'места', 'мест')}</span></div></div>
    </article>`;
  }
  function renderRoutesIndex() {
    $('routesIndex').hidden = false; $('routeDetail').hidden = true;
    const cols = S.data.collections || [];
    const routes = cols.filter((c) => (c.kind || 'route') === 'route');
    const lists = cols.filter((c) => c.kind === 'collection');
    $('routesGrid').innerHTML = routes.map(routeCardHtml).join('');
    $('collectionsGrid').innerHTML = lists.map(routeCardHtml).join('');
    $('collectionsTitle').hidden = !lists.length; $('collectionsGrid').hidden = !lists.length;
    document.querySelectorAll('[data-route]').forEach((el) => el.addEventListener('click', () => (location.hash = `#/routes/${el.dataset.route}`)));
  }
  function renderRoute(id) {
    const c = (S.data.collections || []).find((x) => x.id === id);
    if (!c) return renderRoutesIndex();
    $('routesIndex').hidden = true; const root = $('routeDetail'); root.hidden = false;
    const items = collectionItems(c);
    const isRoute = (c.kind || 'route') === 'route';
    root.innerHTML = `
      <a class="back" href="#/routes">← Все маршруты</a>
      <div class="route-head">
        <div><h1>${esc(c.title)}</h1><p class="lead">${esc(c.description || '')}</p>
          <div class="route-stats">${c.duration ? `<span>⏱ ${esc(c.duration)}</span>` : ''}${c.transport ? `<span>🛵 ${esc(c.transport)}</span>` : ''}${c.budget ? `<span>💸 ${esc(c.budget)}</span>` : ''}<span>${items.length} ${plural(items.length, 'место', 'места', 'мест')}</span></div>
          <div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap"><button class="btn" id="rShare" type="button">↗ Поделиться</button>${isRoute && items.filter(hasGeo).length > 1 ? `<a class="btn" target="_blank" rel="noopener" href="https://www.google.com/maps/dir/${items.filter(hasGeo).map((i) => `${i.latitude},${i.longitude}`).join('/')}">🧭 Открыть маршрут в Google Maps</a>` : ''}</div>
        </div>
        ${items.some(hasGeo) ? '<div class="route-map" id="routeMap"></div>' : ''}
      </div>
      ${isRoute
        ? `<div class="steps">${items.map((i, n) => `<div class="step"><div class="step-n">${n + 1}</div><div class="step-body" data-id="${i.id}"><div><b>${esc(i.title)}</b><div class="card-meta">${esc((CATS[i.category] || {}).label || '')}${i.neighborhood !== 'Other' ? ' · ' + esc(areaLabel(i.neighborhood)) : ''}${hoursToday(i) ? ' · ' + esc(hoursToday(i).text) : ''}</div><div class="step-note">${esc(i.note || highlight(i))}</div></div>${photoOf(i) ? `<img src="${esc(photoOf(i))}" alt="" loading="lazy">` : ''}</div></div>`).join('')}</div>`
        : `<div class="grid">${items.map((i) => cardHtml(i).replace('<div class="card-text">', i.note ? `<div class="card-text">${esc(i.note)} </div><div class="card-text" hidden>` : '<div class="card-text">')).join('')}</div>`}`;
    bindCards(root);
    $('rShare').onclick = () => share(c.title, location.origin + location.pathname + `#/routes/${id}`);
    if (items.some(hasGeo)) {
      if (S.routeMap) { S.routeMap.remove(); S.routeMap = null; }
      const m = S.routeMap = L.map('routeMap', { scrollWheelZoom: false }); tiles().addTo(m);
      const pts = [];
      items.forEach((i, n) => { if (!hasGeo(i)) return; pts.push([i.latitude, i.longitude]);
        const mk = L.marker([i.latitude, i.longitude], { icon: isRoute ? L.divIcon({ className: '', html: `<div class="pin num"><span>${n + 1}</span></div>`, iconSize: [28, 28], iconAnchor: [14, 14], popupAnchor: [0, -14] }) : pinIcon(i) }).addTo(m);
        mk.bindPopup(() => popupHtml(i), { closeButton: false });
        mk.on('popupopen', (e) => { const el = e.popup.getElement().querySelector('.pop'); el && el.addEventListener('click', () => openDetail(i.id, true)); });
      });
      if (isRoute && pts.length > 1) L.polyline(pts, { color: '#c8502a', weight: 3, opacity: .7, dashArray: '6 6' }).addTo(m);
      m.fitBounds(L.latLngBounds(pts).pad(0.2));
    }
  }

  // ---------- Wiki ----------
  function wikiSummary(a) { return (a.summary || a.content.replace(/^#.*$/m, '').replace(/!\[[^\]]*\]\([^)]*\)/g, '').replace(/[#*>\[\]_`]/g, '').trim().split('\n').find((l) => l.trim().length > 30) || '').trim(); }
  function renderWikiIndex() {
    $('wikiIndex').hidden = false; $('wikiArticle').hidden = true;
    const list = S.wiki.filter((a) => matches({ title: a.title, description: a.content }, S.q));
    $('wikiGrid').innerHTML = list.map((a) => `<div class="wiki-card" data-wiki="${esc(a.id)}"><div class="wiki-ico">${a.emoji || '📄'}</div><div><h3>${esc(a.title)}</h3><p>${esc(wikiSummary(a))}</p></div></div>`).join('') || '<div class="empty">Ничего не найдено</div>';
    document.querySelectorAll('[data-wiki]').forEach((el) => el.addEventListener('click', () => (location.hash = `#/wiki/${el.dataset.wiki}`)));
  }
  function renderWikiArticle(id) {
    const idx = S.wiki.findIndex((a) => a.id === id);
    if (idx < 0) return renderWikiIndex();
    const a = S.wiki[idx];
    $('wikiIndex').hidden = true; const root = $('wikiArticle'); root.hidden = false;
    let md = a.content.replace(/^> \[!(WARNING|CAUTION|TIP|NOTE)\]\s*\n((?:> ?.*\n?)+)/gm, (_, kind, body) => `<div class="alert alert-${kind.toLowerCase()}"><p>${esc(body.replace(/^> ?/gm, '').trim())}</p></div>\n`);
    md = md.replace(/!\[[^\]]*\]\(https:\/\/images\.unsplash\.com[^)]*\)\n?/g, ''); // stock images add nothing
    const html = marked.parse(md, { breaks: false });
    const related = (a.related || []).map((i) => S.byId.get(i)).filter(Boolean);
    const prev = S.wiki[idx - 1], next = S.wiki[idx + 1];
    root.innerHTML = `<a class="back" href="#/wiki">← Справочник</a>
      <div class="prose">${html}</div>
      <div style="margin-top:20px"><button class="btn" id="wShare" type="button">↗ Поделиться</button></div>
      ${related.length ? `<div class="related"><h2>Места по теме</h2><div class="list-simple">${related.map(cardHtml).join('')}</div></div>` : ''}
      <div class="article-nav"><span>${prev ? `<a href="#/wiki/${prev.id}">← ${esc(prev.title)}</a>` : ''}</span><span>${next ? `<a href="#/wiki/${next.id}">${esc(next.title)} →</a>` : ''}</span></div>`;
    root.querySelectorAll('a[href^="#wiki:"]').forEach((l) => (l.href = '#/wiki/' + l.getAttribute('href').split(':')[1]));
    root.querySelectorAll('.prose a[href^="http"]').forEach((l) => { l.target = '_blank'; l.rel = 'noopener'; });
    bindCards(root);
    $('wShare').onclick = () => share(a.title, location.origin + location.pathname + `#/wiki/${a.id}`);
    window.scrollTo({ top: 0 });
  }

  // ---------- Init ----------
  function bindUI() {
    const si = $('searchInput');
    let t;
    si.addEventListener('input', () => { clearTimeout(t); t = setTimeout(() => { S.q = si.value.trim(); S.page = 1; $('searchClear').hidden = !S.q;
      if (S.view === 'wiki') { renderWikiIndex(); location.hash.startsWith('#/wiki/') && (location.hash = '#/wiki'); }
      else if (S.view === 'events') renderEvents();
      else if (S.view === 'map') { syncUrl(); renderMap(); }
      else { if (S.view !== 'places') { location.hash = placesHash(); } else { syncUrl(); renderPlaces(); } }
    }, 160); });
    si.addEventListener('keydown', (e) => { if (e.key === 'Escape') { si.value = ''; si.dispatchEvent(new Event('input')); si.blur(); } });
    $('searchClear').addEventListener('click', () => { si.value = ''; si.dispatchEvent(new Event('input')); si.focus(); });
    $('areaSelect').addEventListener('change', (e) => { S.area = e.target.value; S.page = 1; syncUrl(); renderPlaces(); });
    $('vegToggle').addEventListener('change', (e) => { S.veg = e.target.checked; S.page = 1; syncUrl(); renderPlaces(); });
    $('sortSelect').addEventListener('change', (e) => { S.sort = e.target.value; if (S.sort === 'distance' && !S.me) return locate(renderPlaces); syncUrl(); renderPlaces(); });
    $('nearBtn').addEventListener('click', () => S.me ? (S.me = null, S.sort = 'popular', syncControls(), syncUrl(), renderPlaces()) : locate(renderPlaces));
    $('mapNearBtn').addEventListener('click', () => locate(() => { renderMap(); S.map.setView([S.me.lat, S.me.lng], 14); }));
    $('moreBtn').addEventListener('click', () => { S.page++; renderPlaces(); });
    $('eventSeg').querySelectorAll('button').forEach((b) => b.addEventListener('click', () => { S.eventsMode = b.dataset.mode; renderEvents(); }));
    $('detailBackdrop').addEventListener('click', () => closeDetail(true));
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !$('detail').hidden) closeDetail(true); if (e.key === '/' && document.activeElement !== si) { e.preventDefault(); si.focus(); } });
    window.addEventListener('hashchange', route);
  }

  async function init() {
    bindUI();
    try {
      const [data, wiki] = await Promise.all([fetch('static/data.json').then((r) => r.json()), fetch('static/wiki.json').then((r) => r.json()).catch(() => [])]);
      S.data = data; S.items = data.items; S.wiki = wiki;
      for (const i of S.items) {
        S.byId.set(i.id, i);
        if (typeof i.opening_hours === 'string' && i.opening_hours.startsWith('{')) { try { i.opening_hours = JSON.parse(i.opening_hours); } catch { i.opening_hours = null; } }
        else if (typeof i.opening_hours === 'string') i.opening_hours = null;
      }
      // areas by count
      const ac = {};
      for (const i of placeItems()) if (i.neighborhood && i.neighborhood !== 'Other') ac[i.neighborhood] = (ac[i.neighborhood] || 0) + 1;
      $('areaSelect').innerHTML = '<option value="">Все районы</option>' + Object.entries(ac).sort((a, b) => b[1] - a[1]).map(([k, n]) => `<option value="${esc(k)}">${esc(areaLabel(k))} (${n})</option>`).join('');
    } catch (e) {
      $('placesGrid').innerHTML = '<div class="empty"><b>Не удалось загрузить данные</b>Обновите страницу</div>';
      console.error(e); return;
    }
    route();
  }
  window.__cm = S; // debugging handle
  init();
})();
