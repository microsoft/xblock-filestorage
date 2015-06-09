import textwrap

import urllib2
import json
import logging
LOG = logging.getLogger(__name__)
import re

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

# Helper class to manage filtering the document URL depending upon how it is intented to be used
class filter():
    # match the url against url patterns for various services to determine the source of the document and then convert the url into an embed code depending upon whether the service supports OEmbed protocol or
    # whether we can do the conversion using just string replacement.
    @staticmethod
    def get_embed_code(url):
        url = url.strip()

        youtube_regex = '(https?:\/\/(www\.)?)(youtube\.com|youtu\.be|youtube\.googleapis.com)\/(?:embed\/|v\/|watch\?v=|watch\?.+&amp;v=|watch\?.+&v=)?((\w|-){11})(.*?)'
        matched = re.match(youtube_regex, url)

        if matched is not None:
            embed_url = "http://www.youtube.com/oembed?url=" + matched.group() + "&format=json";
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']

        odb_regex = 'https?:\/\/((\w|-)+)-my.sharepoint.com\/'
        matched = re.match(odb_regex, url)

        if matched is not None:
            document_url = url.replace('action=default', 'action=embedview')
            LOG.info('odb: ')
            LOG.info(document_url)
            return EMBED_CODE_TEMPLATE.format(document_url)

        onedrive_regex = '(https?:\/\/(onedrive\.)?)(live\.com)'
        matched = re.match(onedrive_regex, url)

        if matched is not None:
            document_url = url.replace('view.aspx', 'embed').replace('redir', 'embed')
            return EMBED_CODE_TEMPLATE.format(document_url)

        google_document_regex = '(https?:\/\/(docs\.)?)(google\.com)\/(document|spreadsheets)'
        matched = re.match(google_document_regex, url)

        if matched is not None:
            return '<iframe src="' + url + '?embedded=true"></iframe>'

        google_presentation_regex = '(https?:\/\/(docs\.)?)(google\.com)\/(presentation)'
        matched = re.match(google_presentation_regex, url)

        if matched is not None:
            embed_code = EMBED_CODE_TEMPLATE.format(url.replace('pub', 'embed'))
            return embed_code

        ted_regex = '(https?:\/\/(www\.)?)(ted\.com)\/talks'
        matched = re.match(ted_regex, url)

        if matched is not None:
            embed_url = "http://www.ted.com/services/v1/oembed.json?url=" + url
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']

        vimeo_regex = 'https?:\/\/(www\.)?vimeo\.com\/'
        matched = re.match(vimeo_regex, url)

        if matched is not None:
            embed_url = "https://vimeo.com/api/oembed.json?url=" + url
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']

        office_mix_regex = '(https?:\/\/(www\.)?)(mix\.office\.com)/watch'
        matched = re.match(office_mix_regex, url)

        if matched is not None:
            embed_url = "https://mix.office.com/oembed/?url=" + url
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']

        slideshare_regex = 'https?:\/\/(www\.)?slideshare\.net'
        matched = re.match(slideshare_regex, url)

        if matched is not None:
            embed_url = "http://www.slideshare.net/api/oembed/2?url=" + url + "&format=json"
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']

        issuu_regex = 'https?:\/\/(www\.)?issuu\.com'
        matched = re.match(issuu_regex, url)

        if matched is not None:
            embed_url = "http://issuu.com/oembed?url=" + url + "&format=json"
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']

        screenr_regex = 'https?:\/\/(www\.)?screenr\.com'
        matched = re.match(screenr_regex, url)

        if matched is not None:
            embed_url = "http://www.screenr.com/api/oembed.json?url=" + url + "&format=json"
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']

        soundcloud_regex = 'https?:\/\/(www\.)?soundcloud\.com'
        matched = re.match(soundcloud_regex, url)

        if matched is not None:
            embed_url = "http://soundcloud.com/oembed?url=" + url + "&format=json"
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']

        box_regex = 'https?:\/\/(app\.)?box\.com'
        matched = re.match(box_regex, url)

        if matched is not None:
            embed_code = EMBED_CODE_TEMPLATE.format(url.replace('/s/', '/embed/preview/'))
            return embed_code

        return EMBED_CODE_TEMPLATE.format(url)

    # match the url against url patterns for various services to determine the source of the document and then convert the url into a download url
    @staticmethod
    def get_download_url(url):
        url = url.strip()

        odb_regex = 'https?:\/\/((\w|-)+)-my.sharepoint.com\/'
        matched = re.match(odb_regex, url)

        if matched is not None:
            download_url = url.replace('WopiFrame', 'download').replace('sourcedoc', 'UniqueId')
            return download_url

        onedrive_regex = '(https?:\/\/(onedrive\.)?)(live\.com)'
        matched = re.match(onedrive_regex, url)

        if matched is not None:
            download_url = url.replace('\/embed', '\/download')
            return download_url

        dropbox_regex = 'https?:\/\/(www\.)?dropbox\.com'
        matched = re.match(dropbox_regex, url)

        if matched is not None:
            download_url = url.replace('dl=0', 'dl=1')
            return download_url

        return url
