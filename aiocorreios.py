from bs4 import BeautifulSoup

ENDPOINT = 'https://www2.correios.com.br/sistemas/rastreamento/ctrl/ctrlRastreamento.cfm'


def __make_request(session, tracking_id):
    payload = {
        'acao': 'track',
        'objetos': tracking_id,
        'btnPesq': 'Buscar'
    }

    return session.post(ENDPOINT, data=payload)


async def __make_soup(response):
    if type(response) == str:
        return BeautifulSoup(response, 'html.parser')

    return BeautifulSoup(await response.text(), 'html.parser')


def __find_href(tag):
    a = tag.find('a')
    if a:
        return a.get('href')


def __get_events(soup):
    events = soup.select('td.sroLbEvent')

    for i, event in enumerate(events):
        events[i] = {
            'event': event.strong.string,
            'link': __find_href(event)
        }

    return events


def __get_info(soup):
    infos = soup.select('td.sroDtEvent')

    for i, info in enumerate(infos):
        info = list(info.stripped_strings)
        infos[i] = {
            'date': info[0],
            'hour': info[1],
            'local': __fix_local(info[2])
        }

    return infos


def __fix_local(local):
    return local.replace('\xa0/\xa0', ' / ')


def _get_events(html):
    soup = BeautifulSoup(html, 'lxml')
    events = __get_events(soup)
    infos =  __get_info(soup)

    full_events = []
    for event, info in zip(events, infos):
        full_events.append({**event, **info})

    return full_events


async def track_package(session, tracking_id):
    async with __make_request(session, tracking_id) as r:
        html = await r.text()

        if 'Aguardando postagem pelo remetente.' in html:
            return

        else:
            return _get_events(html)
