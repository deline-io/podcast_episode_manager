SINGLE_PAGE_META_KEYS = (
    'id', 'title', 'description', 'pub_date',
    'duration_sec', 'file_url', 'tags'
    )

LIST_PAGE_META_KEYS = (
    'id', 'title', 'description', 'pub_date',
    'duration_sec', 'tags'
)


def render_single_jsons(eps):
    espisode_metas = []
    for html, meta in eps:
        single_meta = {'show_note': html}
        for key in SINGLE_PAGE_META_KEYS:
            single_meta[key] = meta[key]
        espisode_metas.append((single_meta['id'], single_meta))

    return espisode_metas


def render_list_json(eps):
    episode_metas = []
    for html, meta in eps:
        list_meta = {}
        for key in LIST_PAGE_META_KEYS:
            list_meta[key] = meta[key]
        episode_metas.append(list_meta)

    return episode_metas
