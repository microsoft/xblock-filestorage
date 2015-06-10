import textwrap

import urllib2
from urllib import urlencode
from urlparse import parse_qs, urlsplit, urlunsplit
import json
import logging
LOG = logging.getLogger(__name__)
import re


# Helper class to map the document URL into a form required for adding to the courseware, depending upon how it is intended to be used
class Filter():
    EMBED_CODE_TEMPLATE = textwrap.dedent("""
        <iframe
            src="{}"
            frameborder="0"
            width="960"
            height="569"
            allowfullscreen="true"
            mozallowfullscreen="true"
            webkitallowfullscreen="true">
        </iframe>
    """)

    # match the url against url patterns for various services to determine the source of the document and then convert the url into an embed code depending upon whether the service supports OEmbed protocol or
    # whether we can do the conversion using just string replacement.
    @staticmethod
    def get_embed_code(url):
        url = url.strip()
        scheme, netloc, path, query_string, fragment = urlsplit(url)
        query_params = parse_qs(query_string)

        # youtube
        youtube_regex = '(https?:\/\/(www\.)?)(youtube\.com|youtu\.be|youtube\.googleapis.com)\/(?:embed\/|v\/|watch\?v=|watch\?.+&amp;v=|watch\?.+&v=)?((\w|-){11})(.*?)'
        matched = re.match(youtube_regex, url)

        if matched is not None:
            embed_url = "http://www.youtube.com/oembed?url=" + matched.group() + "&format=json";
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']

        # OneDrive for Business
        odb_regex = 'https?:\/\/((\w|-)+)-my.sharepoint.com\/'
        matched = re.match(odb_regex, url)

        if matched is not None:
            query_params['action'] = ['embedview']
            new_query_string = urlencode(query_params, doseq=True)
            document_url = urlunsplit((scheme, netloc, path, new_query_string, fragment))            
            
            LOG.info('odb: ')
            LOG.info(document_url)
            return Filter.EMBED_CODE_TEMPLATE.format(document_url)

        # OneDrive (for consumers)
        onedrive_regex = '(https?:\/\/(onedrive\.)?)(live\.com)'
        matched = re.match(onedrive_regex, url)

        if matched is not None:
            document_url = url.replace('view.aspx', 'embed').replace('redir', 'embed')
            return Filter.EMBED_CODE_TEMPLATE.format(document_url)

        # Google doc
        google_document_regex = '(https?:\/\/(docs\.)?)(google\.com)\/(document|spreadsheets)'
        matched = re.match(google_document_regex, url)

        if matched is not None:
            return '<iframe src="' + url + '?embedded=true"></iframe>'

        # Google presentation
        google_presentation_regex = '(https?:\/\/(docs\.)?)(google\.com)\/(presentation)'
        matched = re.match(google_presentation_regex, url)

        if matched is not None:
            embed_code = Filter.EMBED_CODE_TEMPLATE.format(url.replace('pub', 'embed'))
            return embed_code

        # TED talks
        ted_regex = '(https?:\/\/(www\.)?)(ted\.com)\/talks'
        matched = re.match(ted_regex, url)

        if matched is not None:
            embed_url = "http://www.ted.com/services/v1/oembed.json?url=" + url
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']

        # Vimeo videos
        vimeo_regex = 'https?:\/\/(www\.)?vimeo\.com\/'
        matched = re.match(vimeo_regex, url)

        if matched is not None:
            embed_url = "https://vimeo.com/api/oembed.json?url=" + url
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']

        # Office Mix
        office_mix_regex = '(https?:\/\/(www\.)?)(mix\.office\.com)/watch'
        matched = re.match(office_mix_regex, url)

        if matched is not None:
            embed_url = "https://mix.office.com/oembed/?url=" + url
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']

        # SlideShare decks
        slideshare_regex = 'https?:\/\/(www\.)?slideshare\.net'
        matched = re.match(slideshare_regex, url)

        if matched is not None:
            embed_url = "http://www.slideshare.net/api/oembed/2?url=" + url + "&format=json"
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']

        # Issuu
        issuu_regex = 'https?:\/\/(www\.)?issuu\.com'
        matched = re.match(issuu_regex, url)

        if matched is not None:
            embed_url = "http://issuu.com/oembed?url=" + url + "&format=json"
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']

        # Screenr
        screenr_regex = 'https?:\/\/(www\.)?screenr\.com'
        matched = re.match(screenr_regex, url)

        if matched is not None:
            embed_url = "http://www.screenr.com/api/oembed.json?url=" + url + "&format=json"
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']

        # Soundcloud
        soundcloud_regex = 'https?:\/\/(www\.)?soundcloud\.com'
        matched = re.match(soundcloud_regex, url)

        if matched is not None:
            embed_url = "http://soundcloud.com/oembed?url=" + url + "&format=json"
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']

        # Box.com files
        box_regex = 'https?:\/\/(app\.)?box\.com'
        matched = re.match(box_regex, url)

        if matched is not None:
            embed_code = Filter.EMBED_CODE_TEMPLATE.format(url.replace('/s/', '/embed/preview/'))
            return embed_code

        return Filter.EMBED_CODE_TEMPLATE.format(url)

    # match the url against url patterns for various services to determine the source of the document and then convert the url into a download url
    @staticmethod
    def get_download_url(url):
        url = url.strip()

        # OneDrive for Business
        odb_regex = 'https?:\/\/((\w|-)+)-my.sharepoint.com\/'
        matched = re.match(odb_regex, url)

        if matched is not None:
            download_url = url.replace('WopiFrame', 'download').replace('sourcedoc', 'UniqueId')
            return download_url

        # OneDrive (for consumers)
        onedrive_regex = '(https?:\/\/(onedrive\.)?)(live\.com)'
        matched = re.match(onedrive_regex, url)

        if matched is not None:
            download_url = url.replace('\/embed', '\/download')
            return download_url

        # Dropbox files
        dropbox_regex = 'https?:\/\/(www\.)?dropbox\.com'
        matched = re.match(dropbox_regex, url)

        if matched is not None:
            download_url = url.replace('dl=0', 'dl=1')
            return download_url

        return url
