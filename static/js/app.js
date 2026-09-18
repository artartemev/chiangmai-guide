/* Chiang Mai community guide — single-page app over static/data.json */
(() => {
  'use strict';

  // ---------- Constants ----------
  // Inline SVG icon set (24px grid, stroke-based). Kept tiny on purpose.
  const PATHS = {
    pin: '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    map: '<path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3z"/><path d="M9 3v15M15 6v15"/>',
    calendar: '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    route: '<circle cx="12" cy="12" r="10"/><path d="m16.2 7.8-2.1 6.3-6.3 2.1 2.1-6.3z"/>',
    book: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
    coffee: '<path d="M17 8h1a4 4 0 1 1 0 8h-1"/><path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"/><path d="M6 2v2M10 2v2M14 2v2"/>',
    leaf: '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10Z"/><path d="M2 21c0-3 1.9-5.4 5.1-6C9.5 14.5 12 13 13 12"/>',
    spa: '<circle cx="12" cy="12" r="3"/><path d="M12 16.5A4.5 4.5 0 1 1 7.5 12 4.5 4.5 0 1 1 12 7.5a4.5 4.5 0 1 1 4.5 4.5 4.5 4.5 0 1 1-4.5 4.5"/>',
    cross: '<circle cx="12" cy="12" r="10"/><path d="M12 8v8M8 12h8"/>',
    laptop: '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M2 20h20"/>',
    bed: '<path d="M2 4v16"/><path d="M2 8h18a2 2 0 0 1 2 2v10"/><path d="M2 17h20"/><path d="M6 8v9"/>',
    mountain: '<path d="m8 3 4 8 5-5 5 15H2L8 3z"/>',
    locate: '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/><circle cx="12" cy="12" r="8"/>',
    star: '<path d="m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z"/>',
    clock: '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    phone: '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>',
    globe: '<circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    share: '<path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/><path d="m16 6-4-4-4 4"/><path d="M12 2v13"/>',
    nav: '<path d="m3 11 19-9-9 19-2-8z"/>',
    chat: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    walk: '<circle cx="13" cy="4" r="1.5"/><path d="m9.5 22 2-8-3-1.5-1 4"/><path d="m14 22-2-6-2.5-2 1-5 3 2 2.5 1"/><path d="M8 9.5 10.5 8"/>',
    money: '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="3"/><path d="M6 12h.01M18 12h.01"/>',
    copy: '<rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
    edit: '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
    trash: '<path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/>',
    upload: '<path d="M12 3v12"/><path d="m7 8 5-5 5 5"/><path d="M4 21h16"/>',
    heart: '<path d="M19 14c1.5-1.5 3-3.2 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.8 0-3 .5-4.5 2-1.5-1.5-2.7-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4 3 5.5l7 7z"/>',
    sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    info: '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
    ticket: '<path d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2z"/><path d="M13 5v2M13 11v2M13 17v2"/>',
    smile: '<circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/>',
  };
  const ico = (name, cls = '') => `<svg class="${cls}" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${PATHS[name] || ''}</svg>`;

  const CATS = {
    cafe_restaurant: { label: 'Еда и кофе', icon: 'coffee', color: '#d97706' },
    nature:          { label: 'Природа', icon: 'leaf', color: '#16a34a' },
    kids:            { label: 'Детям', icon: 'smile', color: '#ea580c' },
    wellness:        { label: 'Спа и здоровье', icon: 'spa', color: '#db2777' },
    services:        { label: 'Сервисы и клиники', icon: 'cross', color: '#2563eb' },
    stay:            { label: 'Жильё', icon: 'bed', color: '#7c3aed' },
    workspace:       { label: 'Коворкинги', icon: 'laptop', color: '#0891b2' },
    hiking_trail:    { label: 'Тропы', icon: 'mountain', color: '#65a30d' },
    event:           { label: 'Событие', icon: 'calendar', color: '#dc2626' },
  };
  const catIcon = (cat) => ico((CATS[cat] || {}).icon || 'pin');
  const CAT_ORDER = ['cafe_restaurant', 'nature', 'kids', 'wellness', 'services', 'workspace', 'stay'];
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

  // ---------- i18n ----------
  const I18N = {
    ru: {
      places: 'Места', map: 'Карта', events: 'Афиша', routes: 'Маршруты', wiki: 'Справочник', wikiShort: 'Справка', saved: 'Сохранённые', about: 'О проекте', support: 'Поддержать проект', copy: 'Скопировать', copiedText: 'Скопировано',
      supportTitle: 'Поддержать проект', supportLead: 'Гид бесплатный и без рекламы. Если он вам помог — можно сказать спасибо любым удобным способом. Деньги идут на сервер, Google Maps API и время на обновление базы.', supportQrHint: 'Отсканируйте QR в банковском приложении', supportBybitHint: 'Внутренний перевод по UID — без комиссии', supportUsdtHint: 'Сеть TRC20 (Tron)', supportSbp: 'Перевод по СБП', supportSbpHint: 'Сбербанк, по номеру телефона', supportThanks: 'Спасибо! Любая сумма — это ещё один вечер, потраченный на разбор чатов вместо чего-то другого 🙂',
      searchPh: 'Кофе, стоматолог, водопад, Нимман…', searchWiki: 'Поиск по справочнику…', searchEvents: 'Поиск по афише…',
      all: 'Все', allAreas: 'Все районы', near: 'Рядом со мной', nearShort: 'Рядом', veg: 'Только veg-friendly', vegShort: 'Veg', openNow: 'Открыто сейчас',
      sortPopular: 'Популярные в чате', sortRating: 'Рейтинг Google', sortNew: 'Новые', sortAlpha: 'По алфавиту', sortDist: 'По расстоянию',
      more: 'Показать ещё', nothing: 'Ничего не нашлось', nothingHint: 'Попробуйте другой запрос или снимите фильтры', onMap: 'на карте', noneHere: 'В этой области нет мест',
      eventsTitle: 'Афиша', eventsLead: 'События из чатов: встречи, лекции, кино, йога, концерты.', upcoming: 'Предстоящие', past: 'Прошедшие', noEvents: 'Пока нет анонсов', noPast: 'Архив пуст', eventsHint: 'Новые события появляются по мере обсуждения в чатах', noDate: 'Без даты',
      routesTitle: 'Маршруты и подборки', routesLead: 'Готовые планы на день и тематические списки — собраны из рекомендаций чата.', routesH: 'Маршруты', collectionsH: 'Подборки', route: 'Маршрут', collection: 'Подборка', allRoutes: '← Все маршруты', openInMaps: 'Открыть маршрут в Google Maps',
      wikiTitle: 'Справочник', wikiLead: 'Визы, жильё, байки, врачи, деньги — короткие практичные статьи для жизни в Чиангмае.', wikiBack: '← Справочник', related: 'Места по теме',
      chatSays: 'Что говорят в чате', prices: 'Цены', tips: 'Советы', desc: 'Описание', address: 'Адрес', hours: 'Часы работы', inWiki: 'В справочнике', nearby: 'Рядом', chatMsgs: 'Сообщения из чата', loading: 'Загрузка…', noMsgs: 'Пока нет сообщений', openTg: 'Открыть в Telegram ↗',
      dirs: 'Маршрут в Google Maps', openOnMap: 'Открыть на карте', venue: 'Место проведения', site: 'Сайт', share: 'Поделиться', save: 'Сохранить', savedOk: 'Сохранено', fromYou: 'от вас', today: 'сегодня', reviews: 'отзывов', register: 'Записаться',
      open: 'Открыто', openUntil: 'до', closed: 'Закрыто', opensAt: 'откроется в', open24: 'Круглосуточно',
      todayIn: 'Сегодня в Чиангмае', openNowN: 'мест открыто сейчас', eventsSoon: 'Ближайшие события', quick: 'Быстрый выбор', qBreakfast: 'Завтрак', qCoffee: 'Кофе', qKids: 'С детьми', qVegan: 'Веган', qNature: 'На природу', qSauna: 'Сауна', qBars: 'Вечером',
      savedTitle: 'Сохранённые места', savedLead: 'Список живёт в этом браузере. Чтобы не потерять — поделитесь ссылкой (например, отправьте себе в Telegram): она откроется на любом устройстве.', savedEmpty: 'Пока пусто — нажмите ♡ на любом месте', shareList: 'Поделиться списком', sharedList: 'Список из ссылки', saveAll: 'Сохранить себе', clear: 'Очистить', copied: 'Ссылка скопирована', listMaps: 'Открыть в Google Maps',
      aboutTitle: 'О проекте', footerMade: 'Сделано в', footerNavito: 'Барахолка NaviTo', footerFeedback: 'Предложить место или правку', locating: 'Определяю местоположение…', noGeo: 'Геолокация недоступна', geoFail: 'Не удалось получить местоположение', farAway: 'Похоже, вы не в Чиангмае — покажу расстояния до города',
      lang: 'EN',
    },
    en: {
      places: 'Places', map: 'Map', events: 'Events', routes: 'Routes', wiki: 'Guide', wikiShort: 'Guide', saved: 'Saved', about: 'About', support: 'Support the project', copy: 'Copy', copiedText: 'Copied',
      supportTitle: 'Support the project', supportLead: 'The guide is free and ad-free. If it helped you, say thanks any way you like. Money goes to hosting, the Google Maps API and the hours spent updating the database.', supportQrHint: 'Scan the QR in your banking app', supportBybitHint: 'Internal transfer by UID — no fee', supportUsdtHint: 'TRC20 network (Tron)', supportSbp: 'SBP transfer (Russia)', supportSbpHint: 'Sberbank, by phone number', supportThanks: 'Thank you! Every bit is one more evening spent digging through chats instead of something else 🙂',
      searchPh: 'Coffee, dentist, waterfall, Nimman…', searchWiki: 'Search the guide…', searchEvents: 'Search events…',
      all: 'All', allAreas: 'All areas', near: 'Near me', nearShort: 'Near me', veg: 'Veg-friendly only', vegShort: 'Veg', openNow: 'Open now',
      sortPopular: 'Popular in chat', sortRating: 'Google rating', sortNew: 'Newest', sortAlpha: 'A–Z', sortDist: 'By distance',
      more: 'Show more', nothing: 'Nothing found', nothingHint: 'Try another query or clear the filters', onMap: 'on the map', noneHere: 'No places in this area',
      eventsTitle: 'Events', eventsLead: 'Meetups, talks, movies, yoga and concerts from the community chats.', upcoming: 'Upcoming', past: 'Past', noEvents: 'No upcoming events yet', noPast: 'Archive is empty', eventsHint: 'New events appear as they are discussed in the chats', noDate: 'No date',
      routesTitle: 'Routes & collections', routesLead: 'Ready-made day plans and themed lists, built from chat recommendations.', routesH: 'Routes', collectionsH: 'Collections', route: 'Route', collection: 'Collection', allRoutes: '← All routes', openInMaps: 'Open route in Google Maps',
      wikiTitle: 'Guide', wikiLead: 'Visas, housing, bikes, doctors, money — short practical articles (in Russian).', wikiBack: '← Guide', related: 'Related places',
      chatSays: 'What the chat says', prices: 'Prices', tips: 'Tips', desc: 'About', address: 'Address', hours: 'Opening hours', inWiki: 'In the guide', nearby: 'Nearby', chatMsgs: 'Chat messages', loading: 'Loading…', noMsgs: 'No messages yet', openTg: 'Open in Telegram ↗',
      dirs: 'Directions in Google Maps', openOnMap: 'Open on Map', venue: 'Venue', site: 'Website', share: 'Share', save: 'Save', savedOk: 'Saved', fromYou: 'from you', today: 'today', reviews: 'reviews', register: 'Register',
      open: 'Open', openUntil: 'until', closed: 'Closed', opensAt: 'opens at', open24: 'Open 24 hours',
      todayIn: 'Today in Chiang Mai', openNowN: 'places open now', eventsSoon: 'Upcoming events', quick: 'Quick picks', qBreakfast: 'Breakfast', qCoffee: 'Coffee', qKids: 'Kids', qVegan: 'Vegan', qNature: 'Nature', qSauna: 'Sauna', qBars: 'Tonight',
      savedTitle: 'Saved places', savedLead: 'The list lives in this browser. To keep it, share the link (e.g. send it to yourself in Telegram) — it opens on any device.', savedEmpty: 'Nothing yet — tap ♡ on any place', shareList: 'Share list', sharedList: 'Shared list', saveAll: 'Save to mine', clear: 'Clear', copied: 'Link copied', listMaps: 'Open in Google Maps',
      aboutTitle: 'About', footerMade: 'Made at', footerNavito: 'NaviTo classifieds', footerFeedback: 'Suggest a place or a fix', locating: 'Locating…', noGeo: 'Geolocation unavailable', geoFail: 'Could not get your location', farAway: 'Looks like you are not in Chiang Mai — showing distance to the city',
      lang: 'RU',
    },
  };
  const CAT_EN = { cafe_restaurant: 'Food & coffee', wellness: 'Spa & wellness', services: 'Services & clinics', stay: 'Stay', workspace: 'Coworking', nature: 'Nature', kids: 'Kids', hiking_trail: 'Trails', event: 'Event' };
  const TAG_EN = { 'кофе': 'coffee', 'завтраки': 'breakfast', 'тайская': 'thai', 'азия': 'asian', 'европа': 'european', 'бары': 'bars', 'с видом': 'with a view', 'веган': 'vegan',
    'массаж и спа': 'massage & spa', 'сауна и ice bath': 'sauna & ice bath', 'йога': 'yoga', 'фитнес и бассейн': 'gym & pool', 'красота': 'beauty',
    'стоматологи': 'dentists', 'ветеринары': 'vets', 'врачи и госпитали': 'doctors & hospitals', 'прокат': 'rentals', 'визы и документы': 'visas & papers', 'воркшопы': 'workshops', 'магазины': 'shops',
    'водопады': 'waterfalls', 'озёра': 'lakes', 'смотровые и горы': 'viewpoints', 'парки и сады': 'parks & gardens', 'храмы': 'temples', 'пещеры и источники': 'caves & hot springs', 'тропы': 'trails',
    'отели': 'hotels', 'кондо и квартиры': 'condos', 'глэмпинги и кемпинг': 'glamping & camping', 'резорты и виллы': 'resorts & villas', 'коворкинги': 'coworking',
    'животные и фермы': 'animals & farms', 'игровые и парки': 'playgrounds & parks', 'кафе с детьми': 'family cafes', 'развитие и творчество': 'activities & science', 'детское здоровье': 'pediatrics' };
  let LANG = 'ru';
  try { LANG = localStorage.getItem('cm_lang') || 'ru'; } catch {} // Russian-speaking community: RU unless switched explicitly
  const t = (k) => (I18N[LANG] && I18N[LANG][k]) || I18N.ru[k] || k;
  const catLabel = (c) => LANG === 'en' ? (CAT_EN[c] || '') : ((CATS[c] || {}).label || '');
  const tagLabel = (x) => LANG === 'en' ? (TAG_EN[x] || x) : x;
  function applyStaticI18n() {
    document.querySelectorAll('[data-i18n]').forEach((el) => { el.textContent = t(el.dataset.i18n); });
    document.querySelectorAll('[data-i18n-ph]').forEach((el) => { el.placeholder = t(el.dataset.i18nPh); });
    $('langBtn').textContent = t('lang');
    document.documentElement.lang = LANG;
  }

  // ---------- opening hours (Bangkok time) ----------
  function bangkokNow() { return new Date(new Date().toLocaleString('en-US', { timeZone: 'Asia/Bangkok' })); }
  function parseRange(str) {
    const parts = str.replace(/\u202f/g, ' ').split(/–|—|-/);
    if (parts.length !== 2) return null;
    const mer = (x) => /AM/i.test(x) ? 'AM' : /PM/i.test(x) ? 'PM' : null;
    let [a, b] = parts.map((x) => x.trim());
    let ma = mer(a), mb = mer(b); if (!ma) ma = mb;
    const toMin = (x, m) => { const mm = x.match(/(\d{1,2})(?::(\d{2}))?/); if (!mm) return null; let h = +mm[1]; const mi = +(mm[2] || 0); if (m === 'PM' && h !== 12) h += 12; if (m === 'AM' && h === 12) h = 0; return h * 60 + mi; };
    const st = toMin(a, ma), en = toMin(b, mb);
    if (st == null || en == null) return null;
    return [st, en <= st ? en + 1440 : en];
  }
  const fmtMin = (m) => `${String(Math.floor((m % 1440) / 60)).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`;
  function openState(item) {
    const h = item.opening_hours; if (!h || typeof h !== 'object') return null;
    const now = bangkokNow(); const d = now.getDay(); const mins = now.getHours() * 60 + now.getMinutes();
    const todayV = h[DAYS[d]], prevV = h[DAYS[(d + 6) % 7]];
    const ranges = (v) => (v && !/24 hours|closed/i.test(v)) ? v.split(',').map(parseRange).filter(Boolean) : [];
    if (prevV) for (const r of ranges(prevV)) if (r[1] > 1440 && mins + 1440 < r[1]) return { open: true, until: r[1] % 1440 };
    if (!todayV) return null;
    if (/24 hours/i.test(todayV)) return { open: true, until: null };
    if (/closed/i.test(todayV)) return { open: false };
    const rs = ranges(todayV);
    for (const r of rs) if (mins >= r[0] && mins < r[1]) return { open: true, until: r[1] % 1440 };
    const next = rs.find((r) => r[0] > mins);
    return next ? { open: false, opensAt: next[0] } : { open: false };
  }
  function openLabel(item) {
    const st = openState(item); if (!st) return '';
    if (st.open) return `<span class="open">${st.until == null ? t('open24') : `${t('open')} ${t('openUntil')} ${fmtMin(st.until)}`}</span>`;
    return `<span class="closed">${t('closed')}${st.opensAt != null ? `, ${t('opensAt')} ${fmtMin(st.opensAt)}` : ''}</span>`;
  }

  // ---------- saved places (localStorage) ----------
  let SAVED = new Set();
  try { SAVED = new Set(JSON.parse(localStorage.getItem('cm_saved') || '[]')); } catch {}
  function persistSaved() { try { localStorage.setItem('cm_saved', JSON.stringify([...SAVED])); } catch {} updateSavedBadge(); }
  function toggleSaved(id) { SAVED.has(id) ? SAVED.delete(id) : SAVED.add(id); persistSaved(); document.querySelectorAll(`.heart[data-save="${id}"]`).forEach((b) => b.classList.toggle('on', SAVED.has(id))); }
  const heartBtn = (id, cls = '') => `<button class="heart ${cls} ${SAVED.has(id) ? 'on' : ''}" data-save="${id}" type="button" aria-label="${t('save')}">${ico('heart')}</button>`;
  function bindHearts(root) { root.querySelectorAll('[data-save]').forEach((b) => b.addEventListener('click', (e) => { e.stopPropagation(); toggleSaved(+b.dataset.save); })); }
  function updateSavedBadge() { const n = SAVED.size; document.querySelectorAll('.saved-count').forEach((el) => { el.textContent = n; el.hidden = !n; }); }

  const AREA_ALIASES = { 'Night Bazaar / Chang Khlan': 'Night Bazaar', 'San Kamphaeng / Doi Saket': 'Doi Saket / San Kamphaeng', 'Mae Taeng / Chiang Dao': 'Chiang Dao / Mae Taeng' };

  // ---------- State ----------
  const S = {
    data: null, items: [], byId: new Map(), reviews: null, wiki: [],
    view: 'places', cat: 'all', tag: '', area: '', q: '', veg: false, open: false, sort: 'popular',
    eventsMode: 'upcoming', page: 1,
    me: null, // {lat, lng}
    map: null, cluster: null, meMarker: null, markers: new Map(),
    detailId: null, detailMap: null, routeMap: null,
    admin: false, // true when app.py answers on localhost — enables edit/hide controls
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
    const ph = `<div class="ph ${cls}">${catIcon(item.category)}</div>`;
    return p
      ? `<img src="${esc(p)}" alt="" loading="lazy" onerror="this.outerHTML=this.dataset.ph" data-ph="${esc(ph)}" class="${cls}">`
      : ph;
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
  function toast(msg, action) {
    const el = $('toast'); el.textContent = msg; el.hidden = false;
    if (action) { const b = document.createElement('button'); b.type = 'button'; b.className = 'toast-btn'; b.textContent = action.label; b.onclick = () => { el.hidden = true; action.fn(); }; el.append(b); }
    clearTimeout(toast._t); toast._t = setTimeout(() => (el.hidden = true), action ? 6000 : 2200);
  }
  function share(title, url) {
    if (navigator.share) navigator.share({ title, url }).catch(() => {});
    else navigator.clipboard.writeText(url).then(() => toast(t('copied')));
  }
  function mapsUrl(item) {
    if (item.location_url) return item.location_url;
    if (hasGeo(item)) return `https://www.google.com/maps/search/?api=1&query=${item.latitude},${item.longitude}`;
    const q = item.venue_name || item.address || item.title;
    if (q) {
      const query = q.toLowerCase().includes('chiang mai') || q.toLowerCase().includes('чиангмай') ? q : `${q}, Chiang Mai`;
      return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}`;
    }
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
  function placesHash() { return buildHash('places', { cat: S.cat !== 'all' ? S.cat : '', tag: S.tag, area: S.area, q: S.q, veg: S.veg ? '1' : '', open: S.open ? '1' : '', sort: S.sort !== 'popular' ? S.sort : '' }); }
  function syncUrl() { if (S.view === 'places' || S.view === 'map') history.replaceState(null, '', S.view === 'map' ? buildHash('map', { cat: S.cat !== 'all' ? S.cat : '', tag: S.tag, q: S.q, veg: S.veg ? '1' : '', open: S.open ? '1' : '' }) : placesHash()); }

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
      S.cat = params.get('cat') || 'all'; S.tag = params.get('tag') || ''; S.area = params.get('area') || ''; S.q = params.get('q') || '';
      S.veg = params.get('veg') === '1'; S.open = params.get('open') === '1'; S.sort = params.get('sort') || 'popular'; S.page = 1;
      showView('places'); syncControls(); renderPlaces();
    } else if (view === 'map') {
      S.cat = params.get('cat') || S.cat; S.tag = params.get('tag') || ''; S.q = params.get('q') || S.q; if (params.has('veg')) S.veg = params.get('veg') === '1'; if (params.has('open')) S.open = params.get('open') === '1';
      showView('map'); syncControls(); renderMap();
    } else if (view === 'events') {
      showView('events'); renderEvents();
    } else if (view === 'routes') {
      showView('routes'); path[1] ? renderRoute(+path[1]) : renderRoutesIndex();
    } else if (view === 'wiki') {
      showView('wiki'); path[1] ? renderWikiArticle(path[1]) : renderWikiIndex();
    } else if (view === 'saved') {
      showView('saved'); renderSaved((params.get('ids') || '').split(',').map(Number).filter(Boolean));
    } else if (view === 'about') {
      showView('about');
    } else if (view === 'support') {
      showView('support');
    } else { location.hash = '#/'; }
  }
  function showView(v) {
    S.view = v;
    document.querySelectorAll('.view').forEach((el) => el.classList.toggle('active', el.id === 'view-' + v));
    document.querySelectorAll('[data-view]').forEach((a) => a.classList.toggle('active', a.dataset.view === v));
    if (v !== 'map') window.scrollTo({ top: 0 });
    $('searchInput').placeholder = v === 'wiki' ? t('searchWiki') : v === 'events' ? t('searchEvents') : t('searchPh');
  }
  function syncControls() {
    $('searchInput').value = S.q; $('searchClear').hidden = !S.q;
    $('areaSelect').value = S.area; $('vegToggle').checked = S.veg; $('sortSelect').value = S.sort;
    const vegOk = S.cat === 'all' || S.cat === 'cafe_restaurant';
    if (!vegOk && S.veg) S.veg = false; // the flag only exists for food places
    $('vegToggleWrap').hidden = !vegOk; $('mapVegWrap').hidden = !vegOk; $('mapVegToggle').checked = S.veg;
    $('openToggle').checked = S.open; $('mapOpenToggle').checked = S.open;
    renderChips('catChips'); renderChips('mapCatChips'); renderChips('mapCatChipsMobile');
    renderTagChips('tagChips'); renderTagChips('mapTagChips'); renderTagChips('mapTagChipsMobile');
    $('nearBtn').classList.toggle('on', !!S.me); $('mapNearBtn').classList.toggle('on', !!S.me);
  }

  // ---------- Filtering ----------
  function placeItems() { return S.items.filter((i) => i.category !== 'event'); }
  function filtered() {
    let list = placeItems().filter((i) => {
      if (S.cat !== 'all') { const g = CAT_GROUP[S.cat] || [S.cat]; if (!g.includes(i.category)) return false; }
      if (S.area && i.neighborhood !== S.area) return false;
      if (S.tag && !(i.tags || []).includes(S.tag)) return false;
      if (S.veg && !i.veg_friendly) return false; // strict: only places known to be veg-friendly
      if (S.open && !(openState(i) || {}).open) return false;
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
    const chip = (key, label, n, icon) => `<button class="chip ${S.cat === key ? 'active' : ''}" data-cat="${key}">${icon ? ico(icon) : ''}${label}<span class="n">${n}</span></button>`;
    el.innerHTML = chip('all', t('all'), total) + CAT_ORDER.map((c) => {
      const g = CAT_GROUP[c] || [c];
      return chip(c, catLabel(c), g.reduce((s, k) => s + (counts[k] || 0), 0), CATS[c].icon);
    }).join('');
    el.querySelectorAll('.chip').forEach((b) => b.addEventListener('click', () => { S.cat = b.dataset.cat; S.tag = ''; S.page = 1; syncControls(); syncUrl(); S.view === 'map' ? renderMap() : renderPlaces(); }));
  }
  function renderTagChips(containerId) {
    const el = $(containerId); if (!el) return;
    if (S.cat === 'all') { el.hidden = true; el.innerHTML = ''; return; }
    const g = CAT_GROUP[S.cat] || [S.cat];
    const counts = {};
    for (const i of placeItems()) if (g.includes(i.category)) for (const t of i.tags || []) counts[t] = (counts[t] || 0) + 1;
    const tags = Object.entries(counts).sort((a, b) => b[1] - a[1]).filter(([, n]) => n >= 3);
    if (tags.length < 2) { el.hidden = true; el.innerHTML = ''; return; }
    el.hidden = false;
    el.innerHTML = `<button class="chip ${S.tag ? '' : 'active'}" data-tag="">${t('all')}</button>` + tags.map(([tg, n]) => `<button class="chip ${S.tag === tg ? 'active' : ''}" data-tag="${esc(tg)}">${esc(tagLabel(tg))}<span class="n">${n}</span></button>`).join('');
    el.querySelectorAll('.chip').forEach((b) => b.addEventListener('click', () => { S.tag = b.dataset.tag; S.page = 1; syncControls(); syncUrl(); S.view === 'map' ? renderMap() : renderPlaces(); }));
  }

  // ---------- Cards ----------
  function cardHtml(item) {
    const c = CATS[item.category] || {};
    const d = distOf(item);
    const price = priceHint(item);
    const ol = openLabel(item);
    return `<article class="card" data-id="${item.id}">
      <div class="card-img">${imgOrPh(item)}${admBtn(item.id)}
        <div class="card-badges"><span class="badge">${catIcon(item.category)}${esc(catLabel(item.category))}</span>${d != null ? `<span class="badge dist">${fmtKm(d)}</span>` : ''}</div>
      </div>
      <div class="card-body">
        <div class="card-title">${esc(item.title)}${heartBtn(item.id, 'heart-card')}</div>
        <div class="card-meta">${item.neighborhood && item.neighborhood !== 'Other' ? `<span>${esc(areaLabel(item.neighborhood))}</span>` : ''}${ol ? `<span class="dot"></span>${ol}` : ''}</div>
        <div class="card-text">${esc(highlight(item))}</div>
        <div class="card-foot">
          ${item.rating ? `<span class="pill rating">★ ${item.rating}</span>` : ''}
          ${price ? `<span class="pill">${esc(price)}</span>` : ''}
          ${item.veg_friendly ? `<span class="pill veg">${ico('leaf')} veg</span>` : ''}
          <span style="margin-left:auto;display:inline-flex;align-items:center;gap:4px">${ico('chat')}${item.review_count || 1}</span>
        </div>
      </div>
    </article>`;
  }
  function bindCards(root) {
    root.querySelectorAll('[data-id]').forEach((el) => el.addEventListener('click', (e) => { if (e.target.closest('a,button')) return; openDetail(+el.dataset.id, true); }));
    bindHearts(root);
    root.querySelectorAll('[data-hide]').forEach((b) => b.addEventListener('click', (e) => { e.stopPropagation(); adminArchive(+b.dataset.hide); }));
  }

  function renderPlaces() {
    const list = filtered();
    const grid = $('placesGrid');
    $('placesCount').textContent = list.length ? `${list.length} ${nPlaces(list.length)}` : '';
    const slice = list.slice(0, PAGE * S.page);
    grid.innerHTML = slice.length ? slice.map(cardHtml).join('') : `<div class="empty"><b>${t('nothing')}</b>${t('nothingHint')}</div>`;
    renderToday();
    bindCards(grid);
    $('placesMore').hidden = list.length <= slice.length;
    // wiki hits for search
    const wh = $('wikiHits');
    if (S.q && S.wiki.length) {
      const hits = S.wiki.filter((a) => matches({ title: a.title, description: a.content }, S.q)).slice(0, 4);
      wh.innerHTML = hits.map((a) => `<a href="#/wiki/${a.id}">${ico('book')} <span>${esc(a.title)}</span></a>`).join('');
      wh.hidden = !hits.length;
    } else wh.hidden = true;
  }
  function plural(n, a, b, c) { const m = n % 10, h = n % 100; return (m === 1 && h !== 11) ? a : (m >= 2 && m <= 4 && (h < 10 || h >= 20)) ? b : c; }
  const nPlaces = (n) => LANG === 'en' ? (n === 1 ? 'place' : 'places') : plural(n, 'место', 'места', 'мест');

  // "Today" panel on the untouched catalogue: what is open, what is on, quick picks
  function renderToday() {
    const el = $('todayBox');
    const pristine = S.cat === 'all' && !S.tag && !S.area && !S.q && !S.veg && !S.open;
    if (!pristine) { el.hidden = true; return; }
    const now = bangkokNow();
    const openN = placeItems().filter((i) => (openState(i) || {}).open).length;
    const today = todayISO();
    const soon = S.items.filter((i) => i.category === 'event' && i.event_iso_date && i.event_iso_date >= today).sort((a, b) => a.event_iso_date.localeCompare(b.event_iso_date)).slice(0, 3);
    const dateStr = now.toLocaleDateString(LANG === 'en' ? 'en-GB' : 'ru-RU', { weekday: 'long', day: 'numeric', month: 'long' });
    const quick = [['qBreakfast', { cat: 'cafe_restaurant', tag: 'завтраки' }], ['qCoffee', { cat: 'cafe_restaurant', tag: 'кофе' }], ['qKids', { cat: 'kids' }], ['qVegan', { cat: 'cafe_restaurant', veg: true }], ['qNature', { cat: 'nature' }], ['qSauna', { cat: 'wellness', tag: 'сауна и ice bath' }], ['qBars', { cat: 'cafe_restaurant', tag: 'бары' }]];
    el.hidden = false;
    el.innerHTML = `<div class="today-head">${ico('sun')}<b>${t('todayIn')}</b><span>${esc(dateStr)}, ${fmtMin(now.getHours() * 60 + now.getMinutes())}</span></div>
      <div class="today-row">
        <button class="today-open" type="button" id="todayOpenBtn"><b>${openN}</b> ${t('openNowN')}</button>
        <div class="today-quick">${quick.map(([k, q]) => `<button class="chip" type="button" data-quick='${JSON.stringify(q)}'>${t(k)}</button>`).join('')}</div>
      </div>
      ${soon.length ? `<div class="today-events"><span class="today-lbl">${t('eventsSoon')}:</span>${soon.map((e) => `<a href="#/place/${e.id}">${ico('calendar')}<span>${esc(e.title)}</span><small>${e.event_iso_date.slice(8, 10)}.${e.event_iso_date.slice(5, 7)}</small></a>`).join('')}</div>` : ''}`;
    $('todayOpenBtn').onclick = () => { S.open = true; S.page = 1; syncControls(); syncUrl(); renderPlaces(); };
    el.querySelectorAll('[data-quick]').forEach((b) => b.addEventListener('click', () => { const q = JSON.parse(b.dataset.quick); S.cat = q.cat || 'all'; S.tag = q.tag || ''; S.veg = !!q.veg; S.page = 1; syncControls(); syncUrl(); renderPlaces(); }));
  }

  // ---------- Saved list ----------
  function renderSaved(sharedIds) {
    const root = $('savedView');
    const shared = sharedIds.length && (sharedIds.length !== SAVED.size || sharedIds.some((i) => !SAVED.has(i)));
    const ids = shared ? sharedIds : [...SAVED];
    const items = ids.map((i) => S.byId.get(i)).filter(Boolean);
    const geo = items.filter(hasGeo);
    root.innerHTML = `<div class="page-head"><h1>${shared ? t('sharedList') : t('savedTitle')}</h1><p class="lead">${t('savedLead')}</p>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        ${items.length ? `<button class="btn" id="svShare" type="button">${ico('share')} ${t('shareList')}</button>` : ''}
        ${shared ? `<button class="btn btn-primary" id="svSaveAll" type="button">${ico('heart')} ${t('saveAll')}</button>` : ''}
        ${geo.length > 1 ? `<a class="btn" target="_blank" rel="noopener" href="https://www.google.com/maps/dir/${geo.map((i) => `${i.latitude},${i.longitude}`).join('/')}">${ico('nav')} ${t('listMaps')}</a>` : ''}
        ${!shared && items.length ? `<button class="btn btn-ghost" id="svClear" type="button">${t('clear')}</button>` : ''}
      </div></div>
      <div class="grid">${items.length ? items.map(cardHtml).join('') : `<div class="empty">${t('savedEmpty')}</div>`}</div>`;
    bindCards(root);
    const link = () => location.origin + location.pathname + '#/saved?ids=' + ids.join(',');
    if ($('svShare')) $('svShare').onclick = () => share(t('savedTitle'), link());
    if ($('svSaveAll')) $('svSaveAll').onclick = () => { ids.forEach((i) => SAVED.add(i)); persistSaved(); location.hash = '#/saved'; };
    if ($('svClear')) $('svClear').onclick = () => { SAVED.clear(); persistSaved(); renderSaved([]); };
  }

  // ---------- Geolocation ----------
  function locate(cb) {
    if (!navigator.geolocation) return toast(t('noGeo'));
    toast(t('locating'));
    navigator.geolocation.getCurrentPosition((p) => {
      S.me = { lat: p.coords.latitude, lng: p.coords.longitude };
      if (km(S.me, { lat: CM_CENTER[0], lng: CM_CENTER[1] }) > 300) toast(t('farAway'));
      S.sort = 'distance'; syncControls(); syncUrl();
      cb && cb();
    }, () => toast(t('geoFail')), { enableHighAccuracy: false, timeout: 8000, maximumAge: 300000 });
  }

  // ---------- Map ----------
  function tiles() {
    return L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>', maxZoom: 19,
    });
  }
  function pinIcon(item) {
    const c = CATS[item.category] || {};
    return L.divIcon({ className: '', html: `<div class="pin" style="background:${c.color || '#888'}"><span>${catIcon(item.category)}</span></div>`, iconSize: [28, 28], iconAnchor: [14, 28], popupAnchor: [0, -26] });
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
    $('mapCount').textContent = `${list.length} ${t('onMap')}`;
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
    return `<div class="pop">${p ? `<img src="${esc(p)}" alt="">` : ''}<div><b>${esc(item.title)}</b><span>${esc(catLabel(item.category))}${item.rating ? ` · ★ ${item.rating}` : ''}${distOf(item) != null ? ` · ${fmtKm(distOf(item))}` : ''}</span></div></div>`;
  }
  function updateMapList() {
    if (S.view !== 'map' || !S.map) return;
    const b = S.map.getBounds();
    const visible = filtered().filter((i) => hasGeo(i) && b.contains([i.latitude, i.longitude])).slice(0, 80);
    const row = (i) => `<div class="map-row" data-id="${i.id}">${imgOrPh(i)}<div><b>${esc(i.title)}</b><span>${esc(catLabel(i.category))}${i.neighborhood && i.neighborhood !== 'Other' ? ' · ' + esc(areaLabel(i.neighborhood)) : ''}${distOf(i) != null ? ' · ' + fmtKm(distOf(i)) : ''}</span></div></div>`;
    const ml = $('mapList');
    ml.innerHTML = visible.length ? visible.map(row).join('') : `<div class="empty">${t('noneHere')}</div>`;
    ml.querySelectorAll('.map-row').forEach((r) => {
      r.addEventListener('mouseenter', () => { const m = S.markers.get(+r.dataset.id); m && m.setZIndexOffset(1000); });
      r.addEventListener('click', () => focusMarker(+r.dataset.id));
    });
    const strip = $('mapStrip');
    strip.innerHTML = visible.slice(0, 30).map((i) => `<div class="strip-card" data-id="${i.id}">${imgOrPh(i)}<div><b>${esc(i.title)}</b><span>${esc(catLabel(i.category))}${distOf(i) != null ? ' · ' + fmtKm(distOf(i)) : ''}</span></div></div>`).join('');
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

    const photos = (item.photos || []).map((x) => x.replace(/^\//, ''));
    $('detailPanel').innerHTML = `
      <button class="d-close" id="dClose" aria-label="Close">✕</button>
      <div class="d-hero" id="dHero">${imgOrPh(item)}</div>
      ${photos.length > 1 ? `<div class="d-gallery" id="dGallery">${photos.map((ph, n) => `<img src="${esc(ph)}" alt="" loading="lazy" data-n="${n}" class="${n === 0 ? 'on' : ''}">`).join('')}</div>` : ''}
      <div class="d-body">
        ${S.admin ? `<div class="adm-bar"><span>#${id}</span><button class="btn btn-sm" id="dEdit" type="button">${ico('edit')} Изменить</button><button class="btn btn-sm adm-danger" id="dHide" type="button">${ico('trash')} Скрыть</button></div>` : ''}
        <div class="d-cat"><span class="cat">${catIcon(item.category)}${esc(catLabel(item.category))}</span>${item.neighborhood && item.neighborhood !== 'Other' ? `<span>·</span><span>${esc(areaLabel(item.neighborhood))}</span>` : ''}${item.google_category ? `<span>·</span><span>${esc(item.google_category)}</span>` : ''}</div>
        <h2 class="d-title">${esc(item.title)}</h2>
        <div class="d-facts">
          ${item.rating ? `<span><b>★ ${item.rating}</b> · ${(item.rating_count || 0).toLocaleString('ru')} ${t('reviews')}</span>` : ''}
          ${d != null ? `<span>${ico('locate')} <b>${fmtKm(d)}</b> ${t('fromYou')}</span>` : ''}
          ${ht ? `<span>${ico('clock')} ${openLabel(item) || `<b>${esc(ht.text)}</b> ${t('today')}`}</span>` : ''}
          ${isEvent && item.event_date ? `<span>${ico('calendar')} <b>${esc(item.event_date)}</b></span>` : ''}
          ${isEvent && item.venue_name ? `<span>${ico('pin')} ${esc(item.venue_name)}</span>` : ''}
          <span>${ico('chat')} ${item.review_count || 1} ${LANG === 'en' ? 'chat messages' : plural(item.review_count || 1, 'сообщение', 'сообщения', 'сообщений') + ' в чате'}</span>
        </div>
        <div class="d-actions">
          ${isEvent && item.registration_url ? `<a class="btn btn-primary" href="${esc(item.registration_url)}" target="_blank" rel="noopener">${esc(item.registration_label || t('register'))}</a>` : ''}
          ${maps ? `<a class="btn ${isEvent && item.registration_url ? '' : 'btn-primary'}" href="${esc(maps)}" target="_blank" rel="noopener">${ico('nav')} ${isEvent ? t('openOnMap') : t('dirs')}</a>` : ''}
          ${item.phone_contact ? `<a class="btn" href="tel:${esc(item.phone_contact.replace(/\s/g, ''))}">${ico('phone')} ${esc(item.phone_contact)}</a>` : ''}
          ${item.website ? `<a class="btn" href="${esc(item.website)}" target="_blank" rel="noopener">${ico(/t\.me\//.test(item.website) ? 'chat' : 'globe')} ${/t\.me\//.test(item.website) ? 'Telegram' : t('site')}</a>` : ''}
          <button class="btn heart-btn ${SAVED.has(id) ? 'on' : ''}" id="dSave" type="button">${ico('heart')} <span>${SAVED.has(id) ? t('savedOk') : t('save')}</span></button>
          <button class="btn" id="dShare" type="button">${ico('share')} ${t('share')}</button>
        </div>
        ${isEvent && (item.venue_name || item.address) ? `
          <div class="d-section">
            <h3>${t('venue')}</h3>
            <div class="d-venue-card">
              <div class="d-venue-name">${ico('pin')} <b>${esc(item.venue_name || item.address)}</b></div>
              ${item.address && item.address !== item.venue_name ? `<div class="d-venue-addr">${esc(item.address)}</div>` : ''}
              ${item.neighborhood && item.neighborhood !== 'Other' ? `<div class="d-venue-area">${esc(areaLabel(item.neighborhood))}</div>` : ''}
              ${maps ? `<div style="margin-top:10px;"><a class="btn btn-sm btn-map" href="${esc(maps)}" target="_blank" rel="noopener">${ico('nav')} ${t('openOnMap')}</a></div>` : ''}
            </div>
          </div>` : ''}
        ${cs.highlights && cs.highlights.length ? `<div class="d-section"><h3>${t('chatSays')}</h3>${list(cs.highlights)}</div>` : ''}
        ${cs.pricing && cs.pricing.length ? `<div class="d-section"><h3>${t('prices')}</h3>${list(cs.pricing)}</div>` : ''}
        ${cs.tips && cs.tips.length ? `<div class="d-section"><h3>${t('tips')}</h3>${list(cs.tips)}</div>` : ''}
        ${item.description ? `<div class="d-section"><h3>${t('desc')}</h3><p>${esc(item.description)}</p></div>` : ''}
        ${hasGeo(item) ? `<div class="d-map" id="dMap"></div>` : ''}
        ${item.address ? `<div class="d-section"><h3>${t('address')}</h3><p>${esc(item.address)}</p></div>` : ''}
        ${item.opening_hours && typeof item.opening_hours === 'object' ? `<div class="d-section"><details class="d-details"><summary>${t('hours')}</summary><div class="hours">${Object.entries(item.opening_hours).map(([k, v]) => `<span class="${ht && ht.day === k ? 'today' : ''}">${DAYS_RU[k] || k}</span><span class="${ht && ht.day === k ? 'today' : ''}">${esc(v)}</span>`).join('')}</div></details></div>` : ''}
        ${related.length ? `<div class="d-section"><h3>${t('inWiki')}</h3><div class="wiki-hits">${related.map((a) => `<a href="#/wiki/${a.id}">${ico('book')} <span>${esc(a.title)}</span></a>`).join('')}</div></div>` : ''}
        ${nearby.length ? `<div class="d-section"><h3>${t('nearby')}</h3><div class="nearby">${nearby.map(({ i, d }) => `<a href="#/place/${i.id}">${imgOrPh(i)}<div><b>${esc(i.title)}</b><span>${esc(catLabel(i.category))}</span></div><span>${fmtKm(d)}</span></a>`).join('')}</div></div>` : ''}
        <div class="d-section"><details class="d-details" id="dReviews"><summary>${t('chatMsgs')} (${item.review_count || 0})</summary><div id="dReviewsBody"><div class="empty">${t('loading')}</div></div></details></div>
      </div>`;
    $('detail').hidden = false;
    document.body.style.overflow = 'hidden';
    $('dClose').onclick = () => closeDetail(true);
    if (S.admin) { $('dEdit').onclick = () => renderEditForm(item); $('dHide').onclick = () => { closeDetail(true); adminArchive(id); }; }
    $('dShare').onclick = () => share(item.title, location.origin + location.pathname + `#/place/${id}`);
    $('dSave').onclick = () => { toggleSaved(id); $('dSave').classList.toggle('on', SAVED.has(id)); $('dSave').querySelector('span').textContent = SAVED.has(id) ? t('savedOk') : t('save'); };
    if ($('dGallery')) $('dGallery').querySelectorAll('img').forEach((im) => im.addEventListener('click', () => { $('dHero').innerHTML = `<img src="${esc(im.src)}" alt="">`; $('dGallery').querySelectorAll('img').forEach((x) => x.classList.toggle('on', x === im)); }));
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
      try { S.reviews = await (await fetch('static/reviews.json', { cache: 'no-cache' })).json(); } catch { S.reviews = {}; }
    }
    const rs = S.reviews[item.id] || [];
    $('dReviewsBody').innerHTML = rs.length ? rs.map((r) => `<div class="review"><div class="review-head"><b>${esc(r.sender_name || 'Аноним')}</b><span>${esc((r.msg_date || '').slice(0, 10))}</span></div><p>${esc(r.review_text)}</p>${r.source_link ? `<a href="${esc(r.source_link)}" target="_blank" rel="noopener">${t('openTg')}</a>` : ''}</div>`).join('') : `<div class="empty">${t('noMsgs')}</div>`;
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

  // ---------- Local admin (app.py on localhost) ----------
  const admBtn = (id) => S.admin ? `<button class="adm-x" data-hide="${id}" type="button" title="Скрыть из гида">${ico('trash')}</button>` : '';
  async function adminApi(path, body, method = 'POST') {
    const r = await fetch('/api/admin/' + path, { method, headers: { 'Content-Type': 'application/json' }, body: body ? JSON.stringify(body) : undefined });
    const j = await r.json().catch(() => ({}));
    if (!r.ok || j.ok === false) throw new Error(j.detail || j.log || r.statusText);
    return j;
  }
  function rerender() {
    syncControls(); // chip counts
    if (S.view === 'places') renderPlaces();
    else if (S.view === 'events') renderEvents();
    else if (S.view === 'map') renderMap();
    else route();
    adminRefreshBadge();
  }
  async function adminRefreshBadge() {
    try { const j = await adminApi('ping', null, 'GET'); $('publishBtn').classList.toggle('dirty', !!j.dirty); } catch {}
  }
  async function adminArchive(id) {
    const item = S.byId.get(id); if (!item) return;
    try { await adminApi(`item/${id}/archive`); } catch (e) { return toast('Ошибка: ' + e.message); }
    S.items = S.items.filter((i) => i.id !== id); S.byId.delete(id);
    rerender();
    toast(`Скрыто: ${item.title}`, { label: 'Отменить', fn: async () => {
      try { await adminApi(`item/${id}/restore`); } catch (e) { return toast('Ошибка: ' + e.message); }
      S.items.push(item); S.items.sort((a, b) => a.id - b.id); S.byId.set(id, item); rerender(); toast('Вернули');
    } });
  }
  function renderEditForm(item) {
    const isEvent = item.category === 'event';
    const areas = [...new Set(S.items.map((i) => i.neighborhood).filter((a) => a && a !== 'Other'))].sort();
    const f = (label, name, val, kind = 'input', extra = '') => `<label class="adm-field"><span>${label}</span>${kind === 'textarea' ? `<textarea name="${name}" rows="4">${esc(val)}</textarea>` : `<input name="${name}" value="${esc(val)}" ${extra}>`}</label>`;
    $('detailPanel').querySelector('.d-body').innerHTML = `
      <form class="adm-form" id="admForm">
        <div class="adm-bar"><span>#${item.id} · редактирование</span></div>
        ${f('Название', 'title', item.title)}
        <label class="adm-field"><span>Категория</span><select name="category">${Object.entries(CATS).map(([k, c]) => `<option value="${k}" ${k === item.category ? 'selected' : ''}>${c.label}</option>`).join('')}</select></label>
        <label class="adm-field"><span>Район</span><input name="neighborhood" list="admAreas" value="${esc(item.neighborhood === 'Other' ? '' : item.neighborhood)}"><datalist id="admAreas">${areas.map((a) => `<option value="${esc(a)}">`).join('')}</datalist></label>
        ${f('Описание', 'description', item.description || '', 'textarea')}
        ${f('Теги (через запятую)', 'tags', (item.tags || []).join(', '))}
        ${isEvent ? f('Дата (как показывать)', 'event_date', item.event_date || '') + f('Дата ISO (для сортировки)', 'event_iso_date', item.event_iso_date || '', 'input', 'placeholder="2026-09-30"') + f('Площадка', 'venue_name', item.venue_name || '') : ''}
        ${f('Ссылка Google Maps', 'location_url', item.location_url || '')}
        ${f('Сайт / Telegram', 'website', item.website || '')}
        ${f('Телефон', 'phone_contact', item.phone_contact || '')}
        ${f('Адрес', 'address', item.address || '')}
        <label class="toggle"><input type="checkbox" name="veg_friendly" ${item.veg_friendly ? 'checked' : ''}><span>Veg-friendly</span></label>
        <div class="d-actions"><button class="btn btn-primary" type="submit">Сохранить</button><button class="btn" type="button" id="admCancel">Отмена</button></div>
      </form>`;
    $('detailPanel').scrollTop = 0;
    $('admCancel').onclick = () => openDetail(item.id, false);
    $('admForm').onsubmit = async (e) => {
      e.preventDefault();
      const fd = new FormData(e.target);
      const patch = {};
      for (const [k, v] of fd.entries()) patch[k] = v.trim();
      patch.tags = patch.tags.split(',').map((x) => x.trim()).filter(Boolean);
      patch.veg_friendly = fd.has('veg_friendly');
      if (!patch.neighborhood) patch.neighborhood = 'Other';
      // only changed fields go to curation.json — untouched ones keep following the pipeline (tags, geocoder)
      const same = (a, b) => JSON.stringify(a ?? '') === JSON.stringify(b ?? '');
      for (const k of Object.keys(patch)) if (same(patch[k], k === 'veg_friendly' ? !!item[k] : k === 'tags' ? item.tags || [] : item[k] || '')) delete patch[k];
      if (!Object.keys(patch).length) return openDetail(item.id, false);
      const btn = e.target.querySelector('[type=submit]'); btn.disabled = true;
      try { await adminApi(`item/${item.id}`, patch, 'PATCH'); } catch (err) { btn.disabled = false; return toast('Ошибка: ' + err.message); }
      Object.assign(item, patch);
      openDetail(item.id, false); rerender(); toast('Сохранено');
    };
  }
  async function adminPublish() {
    const b = $('publishBtn'); b.disabled = true; toast('Публикую…');
    try {
      const j = await adminApi('publish');
      toast(j.nothing ? 'Нечего публиковать' : 'Опубликовано — GitHub Pages обновится через минуту');
    } catch (e) { toast('Ошибка публикации: ' + e.message); console.error(e); }
    b.disabled = false; adminRefreshBadge();
  }
  async function initAdmin() {
    if (!/^(localhost|127\.0\.0\.1)$/.test(location.hostname)) return;
    try { const j = await adminApi('ping', null, 'GET'); if (!j.ok) return; S.admin = true; $('publishBtn').hidden = false; $('publishBtn').classList.toggle('dirty', !!j.dirty); $('publishBtn').onclick = adminPublish; } catch {}
  }

  // ---------- Events ----------
  function renderEvents() {
    const today = todayISO();
    const all = S.items.filter((i) => i.category === 'event' && matches(i, S.q));
    const upcoming = all.filter((i) => !i.event_iso_date || i.event_iso_date >= today).sort((a, b) => (a.event_iso_date || '9999').localeCompare(b.event_iso_date || '9999'));
    const past = all.filter((i) => i.event_iso_date && i.event_iso_date < today).sort((a, b) => b.event_iso_date.localeCompare(a.event_iso_date));
    const list = S.eventsMode === 'upcoming' ? upcoming : past;
    $('eventSeg').querySelectorAll('button').forEach((b) => { b.classList.toggle('active', b.dataset.mode === S.eventsMode); b.textContent = b.dataset.mode === 'upcoming' ? `${t('upcoming')} (${upcoming.length})` : `${t('past')} (${past.length})`; });
    const el = $('eventsList');
    if (!list.length) { el.innerHTML = `<div class="empty"><b>${S.eventsMode === 'upcoming' ? t('noEvents') : t('noPast')}</b>${t('eventsHint')}</div>`; return; }
    let lastMonth = '';
    el.innerHTML = list.map((i) => {
      const dt = i.event_iso_date ? new Date(i.event_iso_date + 'T00:00:00') : null;
      const monthKey = dt ? `${MONTHS_RU[dt.getMonth()]} ${dt.getFullYear()}` : t('noDate');
      const head = monthKey !== lastMonth ? `<div class="event-day">${monthKey}</div>` : '';
      lastMonth = monthKey;
      const p = photoOf(i);
      const mUrl = mapsUrl(i);
      const venueStr = i.venue_name || (i.neighborhood && i.neighborhood !== 'Other' ? areaLabel(i.neighborhood) : '');
      return head + `<div class="event ${S.eventsMode === 'past' ? 'past' : ''}" data-id="${i.id}">
        <div class="event-date">${dt ? `<b>${dt.getDate()}</b><span>${MONTHS_RU[dt.getMonth()]}</span>` : '<b>—</b>'}</div>
        <div class="event-content">
          <div class="event-title">${esc(i.title)}</div>
          <div class="event-meta">
            ${i.event_date ? `<span class="event-meta-item">${ico('calendar')} ${esc(i.event_date)}</span>` : ''}
            ${venueStr ? `<span class="event-meta-item event-venue">${ico('pin')} <b>${esc(venueStr)}</b></span>` : ''}
          </div>
          ${mUrl ? `
            <div class="event-actions">
              <a class="btn btn-sm btn-map" href="${esc(mUrl)}" target="_blank" rel="noopener" onclick="event.stopPropagation()">
                ${ico('nav')} <span>${t('openOnMap')}</span>
              </a>
              ${i.registration_url ? `
                <a class="btn btn-sm btn-ghost" href="${esc(i.registration_url)}" target="_blank" rel="noopener" onclick="event.stopPropagation()">
                  ${ico('ticket')} <span>${esc(i.registration_label || t('register'))}</span>
                </a>` : ''}
            </div>` : ''}
        </div>
        ${p ? `<img class="event-thumb" src="${esc(p)}" alt="" loading="lazy">` : '<span></span>'}${admBtn(i.id)}
      </div>`;
    }).join('');
    bindCards(el);
  }

  // ---------- Routes ----------
  function collectionItems(col) { return (col.items || []).map((x) => ({ ...S.byId.get(x.id), note: x.note })).filter((x) => x.id); }
  function routeCardHtml(c) {
    const items = collectionItems(c);
    const cover = c.cover_image || (items.map(photoOf).find(Boolean));
    const isRoute = (c.kind || 'route') === 'route';
    return `<article class="card route-card" data-route="${c.id}">
      <div class="card-img">${cover ? `<img src="${esc(cover.replace(/^\//, ''))}" alt="" loading="lazy">` : `<div class="ph">${ico('route')}</div>`}</div>
      <div class="card-body"><div class="route-kind">${isRoute ? t('route') : t('collection')} · ${items.length} ${nPlaces(items.length)}</div><h3>${esc(c.title)}</h3><div class="card-text">${esc(c.description || '')}</div>
      <div class="card-foot route-stats">${c.duration ? `<span>${ico('clock')} ${esc(c.duration)}</span>` : ''}${c.transport ? `<span>${ico('walk')} ${esc(c.transport)}</span>` : ''}${c.budget ? `<span>${ico('money')} ${esc(c.budget)}</span>` : ''}</div></div>
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
      <a class="back" href="#/routes">${t('allRoutes')}</a>
      <div class="route-head">
        <div><h1>${esc(c.title)}</h1><p class="lead">${esc(c.description || '')}</p>
          <div class="route-stats">${c.duration ? `<span>${ico('clock')} ${esc(c.duration)}</span>` : ''}${c.transport ? `<span>${ico('walk')} ${esc(c.transport)}</span>` : ''}${c.budget ? `<span>${ico('money')} ${esc(c.budget)}</span>` : ''}<span>${items.length} ${nPlaces(items.length)}</span></div>
          <div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap"><button class="btn" id="rShare" type="button">${ico('share')} ${t('share')}</button>${isRoute && items.filter(hasGeo).length > 1 ? `<a class="btn" target="_blank" rel="noopener" href="https://www.google.com/maps/dir/${items.filter(hasGeo).map((i) => `${i.latitude},${i.longitude}`).join('/')}">${ico('nav')} ${t('openInMaps')}</a>` : ''}</div>
        </div>
        ${items.some(hasGeo) ? '<div class="route-map" id="routeMap"></div>' : ''}
      </div>
      ${isRoute
        ? `<div class="steps">${items.map((i, n) => `<div class="step"><div class="step-n">${n + 1}</div><div class="step-body" data-id="${i.id}"><div><b>${esc(i.title)}</b><div class="card-meta">${esc(catLabel(i.category))}${i.neighborhood !== 'Other' ? ' · ' + esc(areaLabel(i.neighborhood)) : ''}${openLabel(i) ? ' · ' + openLabel(i) : ''}</div><div class="step-note">${esc(i.note || highlight(i))}</div></div>${photoOf(i) ? `<img src="${esc(photoOf(i))}" alt="" loading="lazy">` : ''}</div></div>`).join('')}</div>`
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
    $('wikiGrid').innerHTML = list.map((a) => `<div class="wiki-card" data-wiki="${esc(a.id)}"><div class="wiki-ico">${a.emoji || ico('book')}</div><div><h3>${esc(a.title)}</h3><p>${esc(wikiSummary(a))}</p></div></div>`).join('') || `<div class="empty">${t('nothing')}</div>`;
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
    root.innerHTML = `<a class="back" href="#/wiki">${t('wikiBack')}</a>
      <div class="prose">${html}</div>
      <div style="margin-top:20px"><button class="btn" id="wShare" type="button">${ico('share')} ${t('share')}</button></div>
      ${related.length ? `<div class="related"><h2>${t('related')}</h2><div class="list-simple">${related.map(cardHtml).join('')}</div></div>` : ''}
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
    $('vegToggle').addEventListener('change', (e) => { S.veg = e.target.checked; S.page = 1; syncControls(); syncUrl(); renderPlaces(); });
    $('mapVegToggle').addEventListener('change', (e) => { S.veg = e.target.checked; syncControls(); syncUrl(); renderMap(); });
    $('openToggle').addEventListener('change', (e) => { S.open = e.target.checked; S.page = 1; syncControls(); syncUrl(); renderPlaces(); });
    $('mapOpenToggle').addEventListener('change', (e) => { S.open = e.target.checked; syncControls(); syncUrl(); renderMap(); });
    $('langBtn').addEventListener('click', () => { LANG = LANG === 'ru' ? 'en' : 'ru'; try { localStorage.setItem('cm_lang', LANG); } catch {} applyStaticI18n(); renderMap._fitted = renderMap._fitted; route(); });
    applyStaticI18n(); updateSavedBadge();
    document.querySelectorAll('[data-icon]').forEach((el) => (el.innerHTML = ico(el.dataset.icon)));
    $('sortSelect').addEventListener('change', (e) => { S.sort = e.target.value; if (S.sort === 'distance' && !S.me) return locate(renderPlaces); syncUrl(); renderPlaces(); });
    $('nearBtn').addEventListener('click', () => S.me ? (S.me = null, S.sort = 'popular', syncControls(), syncUrl(), renderPlaces()) : locate(renderPlaces));
    $('mapNearBtn').addEventListener('click', () => locate(() => { renderMap(); S.map.setView([S.me.lat, S.me.lng], 14); }));
    $('moreBtn').addEventListener('click', () => { S.page++; renderPlaces(); });
    $('eventSeg').querySelectorAll('button').forEach((b) => b.addEventListener('click', () => { S.eventsMode = b.dataset.mode; renderEvents(); }));
    $('detailBackdrop').addEventListener('click', () => closeDetail(true));
    document.querySelectorAll('.copy-btn').forEach((b) => b.addEventListener('click', () => navigator.clipboard.writeText(b.dataset.copy).then(() => toast(t('copiedText')))));
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !$('detail').hidden) closeDetail(true); if (e.key === '/' && document.activeElement !== si) { e.preventDefault(); si.focus(); } });
    window.addEventListener('hashchange', route);
  }

  async function init() {
    bindUI();
    try {
      const [data, wiki] = await Promise.all([fetch('static/data.json', { cache: 'no-cache' }).then((r) => r.json()), fetch('static/wiki.json', { cache: 'no-cache' }).then((r) => r.json()).catch(() => [])]);
      S.data = data; S.items = data.items; S.wiki = wiki;
      for (const i of S.items) {
        S.byId.set(i.id, i);
        if (typeof i.opening_hours === 'string' && i.opening_hours.startsWith('{')) { try { i.opening_hours = JSON.parse(i.opening_hours); } catch { i.opening_hours = null; } }
        else if (typeof i.opening_hours === 'string') i.opening_hours = null;
      }
      // areas by count
      const ac = {};
      for (const i of placeItems()) if (i.neighborhood && i.neighborhood !== 'Other') ac[i.neighborhood] = (ac[i.neighborhood] || 0) + 1;
      await initAdmin();
      $('areaSelect').innerHTML = '<option value="" data-i18n="allAreas">Все районы</option>' + Object.entries(ac).sort((a, b) => b[1] - a[1]).map(([k, n]) => `<option value="${esc(k)}">${esc(areaLabel(k))} (${n})</option>`).join('');
    } catch (e) {
      $('placesGrid').innerHTML = '<div class="empty"><b>Не удалось загрузить данные</b>Обновите страницу</div>';
      console.error(e); return;
    }
    route();
  }
  window.__cm = S; // debugging handle
  init();
})();
