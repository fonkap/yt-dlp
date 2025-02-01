from .dplay import DiscoveryPlusBaseIE
from ..utils import ExtractorError
from ..utils.traversal import traverse_obj


class Tele5IE(DiscoveryPlusBaseIE):
    _VALID_URL = r'https?://(?:www\.)?dmax\.marca\.com/(?P<parent_slug>[\w-]+)/(?P<slug_a>[\w-]+)(?:/(?P<slug_b>[\w-]+))?'

    def _real_extract(self, url):
        parent_slug, slug_a, slug_b = self._match_valid_url(url).group('parent_slug', 'slug_a', 'slug_b')

        if not slug_b:
            cms_data = self._download_json(
                f'https://it-api.loma-cms.com/feloma/page/{slug_a}/', slug_a, query={
                    'environment': 'dmaxspain',
                    'parent_slug': parent_slug,
                    'v': '2',
                })
        else:
            cms_data = self._download_json(
                f'https://it-api.loma-cms.com/feloma/videos/{slug_b}/', slug_b, query={
                    'filter[show.slug]': slug_a,
                    'environment': 'dmaxspain',
                    'v': '2',
                })

        video_id = traverse_obj(cms_data, ('blocks', ..., 'videoId'), get_all=False)
        if not video_id:
            raise ExtractorError('Unable to extract video id')

        return self._get_disco_api_info(
            url, video_id, 'public.aurora.enhanced.live', 'es', 'ES')

    def _update_disco_api_headers(self, headers, disco_base, display_id, realm):
        headers.update({
            'x-disco-params': 'realm=%s' % realm,
            'x-disco-client': 'Alps:HyogaPlayer:0.0.0',
            'Authorization': self._get_auth(disco_base, display_id, realm),
        })
