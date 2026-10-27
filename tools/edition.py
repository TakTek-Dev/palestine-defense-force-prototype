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
# second research pass (27 Oct): every month of HaMoked's series, case checks, second sources, guide additions
U = json.load(open(os.path.join(ROOT, 'research', 'news-update.json'), encoding='utf-8'))
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
    'un-coi-west-bank-crimes-against-humanity': 'geneva-human-rights-council-2015',
    'settler-suspects-released-to-house-arrest': 'jerusalem-magistrates-court-2012',
    'brad-lander-olive-volunteers-detained': 'nahalin-village-2015',
    'naqab-demolition-wave': 'al-araqib-shelter-2025',
    'court-lifts-travel-ban-on-prisoners-wife': 'allenby-crossing-2019',
    'eu-condemns-attack-on-diplomats': 'taybeh-village-2018',
    'abu-falah-harvest-attack': 'abu-falah-village-2026',
    'yellow-line-moves-west': 'shujaiyya-ibn-uthman-2017',
    'at-tur-largest-single-demolition': 'at-tur-mount-of-olives-2023',
    'jalud-family-blocked-from-return': 'jalud-village-2026',
    'un-settlement-business-database-214': 'geneva-palais-wilson-2023',
    'netanyahu-un-attack-on-al-jazeera': 'unga-hall-2024',
    'twelve-states-settlement-trade-measures': 'barkan-industrial-zone-2016',
    'adalah-academia-discipline-report': 'mount-scopus-campus-2025',
    'palestine-action-filton-appeal': 'royal-courts-of-justice-2016',
    'east-jerusalem-schools-strike': 'sur-baher-school-2022',
    'tribunal-law-october-7-trials': 'knesset-jerusalem-2025',
    'dcip-forced-to-close': 'al-bireh-downtown-2026',
}

# case files: what the clock or the figure on each card says, and the reporting that belongs to it
CASES = {
    'hussam-abu-safiya': {'since': '2024-12-27', 'clock_label': 'days held without charge', 'photo': 'gaza-al-shifa-surgery-after-2025',
                          'stories': ['abu-safiya-still-held-without-charge', 'wma-protest-detained-health-workers']},
    'bushra-al-tawil': {'figure': '~50', 'figure_label': 'days in solitary; order extended four months on 12 Oct 2026'},
    'ihab-diab': {'since': '2023-12-12', 'until': '2026-08-09', 'clock_label': 'days from his arrest until Israel disclosed his death',
                  'stories': ['ihab-diab-death-confirmed']},
    'walid-ahmad': {'figure': '17', 'figure_label': 'years old; died in Megiddo Prison in March 2025'},
    'mohammed-zalbani': {'figure': '18', 'figure_label': 'years’ sentence; arrested at 13', 'stories': ['children-in-detention-testimonies']},
    'dana-joudeh': {'figure': '2', 'figure_label': 'days after a caesarean birth, released (14 Sep 2026)', 'photo': 'damon-prison-2016',
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
# Dana Joudeh: released 14 Sep 2026 (The Intercept, 10 Oct), confirmed in the second pass.
STATUS_FIX = {}

GUIDE_LINES = {
    'administrative-detention': 'Six-month orders, renewed without limit, on evidence neither the detainee nor the lawyer may see.',
    'military-courts': 'Where West Bank Palestinians are tried, and why almost every case ends in a conviction.',
    'unlawful-combatants-law': 'The 2002 law used to hold people from Gaza, and how long it keeps them from a lawyer and a judge.',
    'children-in-detention': 'How many children are held, where, and on what kind of order.',
    'home-demolitions': 'Permits refused, orders served and the courts that rarely stop a bulldozer.',
    'icj-and-icc': 'The cases at the two courts in The Hague, where they stand and what they can do.',
}

ORG_LINES = {}  # the research carries a line for each; kept as researched

# where a second source gives a different figure or date, the story says so (our wording, from the second pass's notes)
DIFFER = {
    'hebron-mass-displacement': 'OCHA, quoted by UN News, counts more than 3,000 people evacuated since 23 October. Reuters’ figure of about 1,200, with 1,300 more at risk, came a day into the same operation.',
    'olive-harvest-record-attacks': 'France 24’s figure comes from OCHA’s own count, so it confirms the story rather than adding an independent count.',
    'at-tur-largest-single-demolition': 'Silwanic counts 75 people displaced; OCHA counts 69.',
    'dana-joudeh-birth-in-detention': 'The Intercept reports the birth on 12 September, by caesarean section at Rambam Hospital. Middle East Monitor, via Quds Press, reports it on 14 September inside Damon prison.',
    'ips-security-inmates-october-2026': 'Addameer gives the same figures, drawn from the same prison-service data. Its own table of 5 October gives about 9,300.',
    'margaret-owen-arrested-palestine-action': 'She was arrested on 27 September outside the Labour Party conference in Liverpool; this page was filed on 1 October.',
    'gaza-since-ceasefire-toll': 'Bernama gives 1,498 killed as of 13 October; OCHA’s “more than 1,500” is from 22 October.',
    'west-bank-100-arrests-in-a-week': 'Middle East Monitor confirms one day of the sweep, 33 arrests on 10 September, but not the weekly total.',
    'jinba-and-az-zaayyem-demolitions': 'B’Tselem, quoted by Middle East Eye, counts about 176 people displaced in Jinba, 85 of them children; OCHA counts 55.',
    'italy-investigates-katz-flotilla': 'The Times of Israel gives both 11 and 12 officials under investigation.',
}

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
        extra = U['extra_sources'].get(it['id'], [])
        seen = {x['url'] for x in s['sources']}
        s['sources'] = s['sources'] + [x for x in extra if x['url'] not in seen]
        s['verified'] = it.get('confidence') == 'verified' or len({x['outlet'] for x in s['sources']}) > 1
        if it['id'] in DIFFER:
            s['differ'] = DIFFER[it['id']]
        if PHOTO.get(it['id']):
            s['photo'] = PHOTO[it['id']]
        stories[it['id']] = s
    by_date = sorted(stories, key=lambda i: (stories[i]['date'], i), reverse=True)

    by_month = {c['as_of']: c for c in N['custody']}
    for c in U['custody_monthly']:
        by_month.setdefault(c['as_of'], c)
    cus = sorted(by_month.values(), key=lambda c: c['as_of'])
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
        chk = U['case_checks'].get(c['id'], {})
        tl = list(x['timeline'])
        if c['id'] == 'dana-joudeh' and chk.get('released'):
            tl = [t for t in tl if t['date'] not in ('2026-09-14', '2026-09-15')]
            tl.append({'date': chk['release_date'], 'event': 'Taken back to prison to process her release, and released the same day with her baby',
                       'source_url': chk['source_url']})
            x['status'] = 'released'
        for add in (chk.get('latest_event'), chk.get('add_timeline')):
            if add:
                tl.append(add)
        x['timeline'] = sorted(tl, key=lambda t: t['date'])
        if chk.get('note'):
            x['check_note'] = chk['note']
        cases.append(x)

    adds = {}
    for a in U['explainer_additions']:
        adds.setdefault(a['explainer_id'], []).append({'text': a['text'], 'source_url': a['source_url']})
    guides = [{'id': e['id'], 'title': e['title'], 'line': GUIDE_LINES.get(e['id'], ''), 'points': e['points'] + adds.get(e['id'], [])}
              for e in N['explainers']]
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
