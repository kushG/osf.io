import copy
import webcolors

COLORBREWER_COLORS = [(166, 206, 227), (31, 120, 180), (178, 223, 138), (51, 160, 44), (251, 154, 153), (227, 26, 28), (253, 191, 111), (255, 127, 0), (202, 178, 214), (106, 61, 154), (255, 255, 153), (177, 89, 40)]


from werkzeug.contrib.atom import AtomFeed


def build_query(q='*', start=0, size=10, sort=None):
    query = {
        'query': build_query_string(q),
        'from': start,
        'size': size,
    }

    if sort:
        query['sort'] = [
            {
                sort: 'desc'
            }
        ]

    return query


def build_query_string(q):
    return {
        'query_string': {
            'default_field': '_all',
            'query': q,
            'analyze_wildcard': True,
            'lenient': True  # TODO, may not want to do this
        }
    }


def generate_color():
    # TODO - this might not be the optimal way - copy is expensive
    colors_to_generate = copy.copy(COLORBREWER_COLORS)
    colors_used = []

    while True:
        try:
            color = colors_to_generate.pop(0)
            colors_used.append(color)
        except IndexError:
            new_colors = get_new_colors(colors_used)
            colors_to_generate = new_colors
            colors_used = []
        yield webcolors.rgb_to_hex(color)


def calculate_distance_between_colors(color1, color2):
    """ Takes 2 color tupes and returns the average between them
    """
    return ((color1[0] + color2[0]) / 2, (color1[1] + color2[1]) / 2, (color1[2] + color2[2]) / 2)


def get_new_colors(colors_used):
    new_colors = []
    for i in xrange(len(colors_used) - 1):
        new_colors.append(calculate_distance_between_colors(colors_used[i], colors_used[i + 1]))

    return new_colors


def create_atom_feed(name, data, query, size, start, url, to_atom):
    if query == '*':
        title_query = 'All'
    else:
        title_query = query

    title = '{name}: Atom Feed for query: "{title_query}"'.format(name=name, title_query=title_query)
    author = 'COS'

    links = [
        {'href': '{url}?page=1'.format(url=url), 'rel': 'first'},
        {'href': '{url}?page={page}'.format(url=url, page=(start / size) + 2), 'rel': 'next'},
        {'href': '{url}?page={page}'.format(url=url, page=(start / size)), 'rel': 'previous'}
    ]

    links = links[1:-1] if (start / size) == 0 else links

    feed = AtomFeed(
        title=title,
        feed_url=url,
        author=author,
        links=links
    )

    for doc in data:
        feed.add(**to_atom(doc))

    return feed
