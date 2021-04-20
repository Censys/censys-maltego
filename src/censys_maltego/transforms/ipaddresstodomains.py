from canari.maltego.entities import Domain, IPv4Address
from canari.maltego.transform import Transform
from canari.maltego.message import MaltegoException
from canari.framework import EnableDebugWindow, RequestFilter

from censys_maltego.transforms.common.utils import check_api_creds

__author__ = "Censys Team"
__copyright__ = "Copyright 2021, censys_maltego Project"
__credits__ = ["Art Sturdevant", "Aidan Holland"]

__license__ = "GPLv3"
__version__ = "0.1"
__maintainer__ = "Censys Team"
__email__ = "support@censys.io"
__status__ = "Development"

FIELDS = ["443.https.tls.certificate.parsed.names"]


@RequestFilter(check_api_creds)
@EnableDebugWindow
class IPAddressToDomains(Transform):
    """IPv4 Address to Domains."""

    # The transform input entity type.
    input_type = IPv4Address

    def do_transform(self, request, response, config):
        from censys import CensysIPv4

        c = CensysIPv4()
        # c = CensysIPv4(config["censys.local.api_id"], config["censys.local.api_secret"])
        ip = request.entity.value
        res = c.view(ip)
        res = list(
            c.search(
                f"ip: {ip} AND 443.https.tls.certificate.parsed.fingerprint_sha256: *",
                fields=FIELDS,
                max_records=1,
            )
        )
        if len(res) == 0:
            raise MaltegoException(f"No search results found for {ip}")

        result = res[0]

        domains = result.get("443.https.tls.certificate.parsed.names")

        if len(domains) == 0:
            raise MaltegoException(f"No Domains found for {ip}")

        for domain in domains:
            response += Domain(domain)

        return response

    def on_terminate(self):
        """This method gets called when transform execution is prematurely terminated. It is only applicable for local
        transforms. It can be excluded if you don't need it."""
        pass
