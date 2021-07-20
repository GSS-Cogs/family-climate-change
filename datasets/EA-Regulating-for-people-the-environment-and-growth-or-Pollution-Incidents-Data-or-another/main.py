# +
from dateutil.parser import parse
from gssutils import *
from gssutils.metadata.dcat import Distribution
from lxml import html
import mimetypes
from urllib.parse import urljoin, urlparse

def patch(scraper):
    """
    Get the govuk scraper working with datasets incorrectly added via json["details"] key
    see: https://www.gov.uk/api/content/government/publications/regulating-for-people-the-environment-and-growth
    
    LEAVE THIS ALONE: Will add a card to remove this when we implement a proper solution in gssutils.
    """

    final_url = False
    uri_components = urlparse(scraper.uri)
    content_api_path = uri_components.path
    while not final_url:
        metadata = scraper.session.get(f'https://www.gov.uk/api/content/{content_api_path}').json()
        schema = metadata['schema_name']
        if schema == 'redirect':
            if 'redirects' in metadata and len(metadata['redirects']) > 0:
                content_api_path = metadata['redirects'][0]['destination']
            else:
                logging.error('Content API response is a redirect, but no redirection found.')
        else:
            final_url = True
            
    # Extend it with missing distributions
    html_from_json_details = html.fromstring(str(metadata["details"]))
    
    for distro_uri in html_from_json_details.xpath("//p/a/@href"):
        uri_components = urlparse(distro_uri)
        content_api_path = uri_components.path
        distro_metadata = scraper.session.get(f'https://www.gov.uk/api/content/{content_api_path}').json()

        for distro_doc in distro_metadata["details"]["attachments"]:
            
            dist = Distribution(scraper)
            dist.title = distro_doc["title"]
            dist.downloadURL = distro_doc["url"]
            dist.mediaType, _ = mimetypes.guess_type(dist.downloadURL)
            dist.issued = parse(distro_metadata["first_published_at"])
            dist.modified = parse(distro_metadata["public_updated_at"])
            
            scraper.distributions.append(dist)
    
metadata = Scraper(seed="info.json")
patch(metadata)

metadata
# -

distribution = metadata.distribution(title = lambda x: "Pollution incidents data" in x, latest = True)
distribution


