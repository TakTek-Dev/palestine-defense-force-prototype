"""Compose tools/edition.json from research/news.json.

python -I tools/edition.py

research/news.json is the sourced research (every item checked against an opened page). This script
decides what the front page shows and in what order, which photograph goes with what, and adds the
small framing lines guides and cases need. It writes no fact of its own: every number below restates
a sourced figure in research/news.json.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = json.load(open(os.path.join(ROOT, 'research', 'news.json'), encoding='utf-8'))
TODAY = '2026-10-27'

# photographs: only where the picture honestly shows the place or the institution in the story
PHOTO = {
    'hamoked-gaza-whereabouts-petition-deleted': 'jerusalem-supreme-court-2018',
    'hebron-mass-displacement': 'hebron-shuhada-street-2016',
    'olive-harvest-record-attacks': 'qaffin-olive-harvest-2008',
    'gaza-since-ceasefire-toll': 'gaza-displacement-2025',
    'unicef-children-killed-since-ceasefire': 'gaza-return-ceasefire-2025',
    'icc-wins-sakharov-prize': 'hague-icc-2024',
    'pps-2000-children-detained': 'ofer-prison-2025',
    'dana-joudeh-birth-in-detention': 'damon-prison-entrance-2017',
    'wma-protest-detained-health-workers': 'gaza-al-shifa-2025',
    'us-sanctions-the-icc': 'hague-icc-dunes-2026',
    'three-years-gaza-toll': 'khan-younis-ruins-2023',
    'abu-safiya-still-held-without-charge': 'beit-lahia-indonesian-hospital-2025',
    'khan-al-ahmar-orders-revived': 'khan-al-ahmar-school-2014',
    'supreme-court-reinstates-arab-lists': 'jerusalem-supreme-court-2009',
    'ips-security-inmates-october-2026': 'ofer-prison-entrance-2017',
    'jinba-and-az-zaayyem-demolitions': 'masafer-yatta-al-fakhit-2025',
    'children-in-detention-testimonies': 'ofer-prison-2012',
    'colombia-withdraws-icj-intervention': 'hague-peace-palace-icj-2025',
    'death-penalty-law-first-test-neveh-tzuf': 'ofer-military-court-2022',
    'west-bank-100-arrests-in-a-week': 'tulkarm-nablus-street-2024',
    'ben-gvir-prison-conditions-policy': 'damon-prison-2010',
    'nicaragua-v-germany-hearings': 'hague-peace-palace-icj-2024',
    'umm-al-khair-volunteer-deported': 'umm-al-kheir-outpost-2025',
    'khirbet-al-tabban-razed': 'khallet-athaba-demolition-feb-2025',
    'citizenship-revocation-petition': 'jerusalem-supreme-court-hall-2017',
    'death-penalty-law-petitions-pending': 'jerusalem-supreme-court-arches-2009',
    'gaza-whereabouts': None,
}

# case files: what the clock or the figure on each card says, and the reporting that belongs to it
CASES = {
    'hussam-abu-safiya': {'since': '2024-12-27', 'clock_label': 'days held without charge', 'photo': 'gaza-al-shifa-surgery-after-2025',
                          'stories': ['abu-safiya-still-held-without-charge', 'wma-protest-detained-health-workers']},
    'bushra-al-tawil': {'figure': '46', 'figure_label': 'days in isolation, reported in October 2026'},
    'ihab-diab': {'since': '2023-12-12', 'until': '2026-08-09', 'clock_label': 'days from his arrest until Israel disclosed his death',
                  'stories': ['ihab-diab-death-confirmed']},
    'walid-ahmad': {'figure': '17', 'figure_label': 'years old; died in Megiddo Prison in March 2025'},
    'mohammed-zalbani': {'figure': '18', 'figure_label': 'years’ sentence; arrested at 13', 'stories': ['children-in-detention-testimonies']},
    'dana-joudeh': {'figure': '2', 'figure_label': 'days after a caesarean birth, returned to prison', 'photo': 'damon-prison-2016',
                    'stories': ['dana-joudeh-birth-in-detention']},
    'mohammad-al-halaseh': {'figure': 'HCJ 76360-04-26', 'figure_label': 'petition pending', 'photo': 'jerusalem-supreme-court-2018',
                            'stories': ['citizenship-revocation-petition']},
    'masafer-yatta-firing-zone-918': {'figure': '969', 'figure_label': 'people displaced in 15 years (OCHA)', 'photo': 'khallet-athaba-demolition-sep-2025',
                                      'stories': ['khirbet-al-tabban-razed', 'jinba-and-az-zaayyem-demolitions']},
    'sarhan-family-batn-al-hawa': {'figure': '~60', 'figure_label': 'families at risk in Batn al-Hawa (Peace Now)', 'photo': 'silwan-from-old-city-wall-2023'},
    'khan-al-ahmar': {'figure': '~200', 'figure_label': 'residents under a revived demolition order', 'photo': 'khan-al-ahmar-2025',
                      'stories': ['khan-al-ahmar-orders-revived']},
    'tubasi-family-jalud': {'figure': '2', 'figure_label': 'homes set alight the night they returned', 'stories': ['jalud-family-blocked-from-return']},
    'death-penalty-law-petition': {'figure': '62–48', 'figure_label': 'Knesset vote, 30 March 2026', 'photo': 'jerusalem-supreme-court-hall-2017',
                                   'stories': ['death-penalty-law-first-test-neveh-tzuf', 'death-penalty-law-petitions-pending']},
}
# Dana Joudeh's release on 15 September was scheduled, not confirmed in the sources: keep her as held on an order.
STATUS_FIX = {'dana-joudeh': 'administrative'}

GUIDE_LINES = {
    'administrative-detention': 'Six-month orders, renewed without limit, on evidence neither the detainee nor the lawyer may see.',
    'military-courts': 'Where West Bank Palestinians are tried, and why almost every case ends in a conviction.',
    'unlawful-combatants-law': 'The 2002 law used to hold people from Gaza, and how long it keeps them from a lawyer and a judge.',
    'children-in-detention': 'How many children are held, where, and on what kind of order.',
    'home-demolitions': 'Permits refused, orders served and the courts that rarely stop a bulldozer.',
    'icj-and-icc': 'The cases at the two courts in The Hague, where they stand and what they can do.',
}

ORG_LINES = {}  # the research carries a line for each; kept as researched

LEAD = 'hamoked-gaza-whereabouts-petition-deleted'
TOP = ['hebron-mass-displacement', 'un-coi-west-bank-crimes-against-humanity', 'abu-safiya-still-held-without-charge',
       'olive-harvest-record-attacks', 'us-sanctions-the-icc']
CASE_ORDER = ['hussam-abu-safiya', 'bushra-al-tawil', 'masafer-yatta-firing-zone-918', 'ihab-diab']
SECTION_ORDER = ['detention', 'courts', 'land', 'international', 'children', 'gaza', 'speech']

KEYS = ('sentenced', 'remand', 'administrative', 'unlawful_combatants')


def month_label(d):
    import datetime as dt
    x = dt.date.fromisoformat(d)
    return x.strftime('%b %Y')


def main():
    stories = {}
    for it in N['items']:
        s = {k: it[k] for k in ('date', 'section', 'place', 'headline', 'dek', 'body', 'sources')}
        s['people'] = it.get('people', [])
        s['figures'] = [{'v': f['value'], 'label': f['label']} for f in it.get('figures', [])]
        s['verified'] = it.get('confidence') == 'verified'
        if PHOTO.get(it['id']):
            s['photo'] = PHOTO[it['id']]
        stories[it['id']] = s
    by_date = sorted(stories, key=lambda i: (stories[i]['date'], i), reverse=True)

    cus = sorted(N['custody'], key=lambda c: c['as_of'])
    series = []
    for c in cus:
        row = {k: c[k] for k in KEYS}
        row['total'] = sum(row.values())
        assert row['total'] == c['total'], c['as_of']
        row['as_of'], row['label'] = c['as_of'], month_label(c['as_of'])
        series.append(row)
    latest = dict(series[-1])
    srcs, seen = [], set()
    for c in reversed(cus):
        if c['source']['url'] not in seen:
            seen.add(c['source']['url'])
            srcs.append(c['source'])
    extra = [{'label': x['label'], 'value': x['value'].split(' (')[0].split(';')[0] if len(x['value']) > 40 else x['value'],
              'as_of': x['as_of'], 'source': x['source']} for x in N['custody_extra']
             if x['label'] in ('Women held', 'Deaths in Israeli custody since 7 October 2023', 'Habeas corpus petitions for missing Gaza detainees',
                               'Children held by the Israel Prison Service', 'West Bank detentions since October 2023',
                               'Unlawful Combatants Law: time before seeing a lawyer')]

    cases = []
    for c in N['cases']:
        x = dict(c)
        x.update(CASES.get(c['id'], {}))
        x['status'] = STATUS_FIX.get(c['id'], c['status'])
        if x['kind'] == 'person' and x['status'] in ('pending_ruling',):
            x['kind_note'] = 'petition'
        x['stories'] = [i for i in x.get('stories', []) if i in stories]
        cases.append(x)

    guides = [{'id': e['id'], 'title': e['title'], 'line': GUIDE_LINES.get(e['id'], ''), 'points': e['points']} for e in N['explainers']]
    orgs = [{'name': o['name'], 'url': o['url'], 'line': o.get('description') or o.get('line', '')} for o in N['orgs'] if o.get('url')]

    sections = {}
    used = {LEAD, *TOP}
    for sl in SECTION_ORDER:
        ids = [i for i in by_date if stories[i]['section'] == sl and i not in used]
        ids.sort(key=lambda i: ('photo' not in stories[i], by_date.index(i)))     # photographed first, then newest
        sections[sl] = ids[:4]
        used.update(ids[:4])

    hab = next(x for x in N['custody_extra'] if x['label'].startswith('Habeas corpus'))
    statement = {'text': 'Families of 114 people taken from Gaza went to court to learn where they were held. 38 were never located.',
                 'who': 'HaMoked habeas corpus petitions, October 2023 to October 2026', 'outlet': hab['source']['outlet'],
                 'url': hab['source']['url'], 'date': hab['as_of']}

    E = {
        'date': TODAY,
        'docket': {'latest': latest, 'series': series, 'source': cus[-1]['source'], 'sources': srcs[:6], 'extra': extra,
                   'note': 'Figures for the first of each month. Remand is HaMoked’s column for people under interrogation, '
                           'awaiting trial and on trial. Only people held by the Israel Prison Service are counted; people held '
                           'in army camps are not.'},
        'stories': stories, 'by_date': by_date, 'cases': cases, 'guides': guides, 'orgs': orgs, 'quote': statement,
        'order': {'lead': LEAD, 'top': TOP, 'cases': CASE_ORDER, 'section_order': SECTION_ORDER, 'sections': sections},
    }
    with open(os.path.join(ROOT, 'tools', 'edition.json'), 'w', encoding='utf-8') as fh:
        json.dump(E, fh, ensure_ascii=False, indent=1)
    print('edition:', len(stories), 'stories,', len(cases), 'cases; latest', latest)


if __name__ == '__main__':
    main()
