import ipaddress
import socket
from urllib.parse import urlparse
from typing import Tuple, Optional, Union

BLOCKED_HOSTNAMES = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "::1",
    "instance-data",
    "metadata.google.internal",
    "169.254.169.254"
}

# NAT64 well-known prefix: 64:ff9b::/96
# These IPv6 addresses embed a public IPv4 in the last 32 bits.
# Python ipaddress marks the whole prefix as is_reserved -- a false positive
# for public IPs translated via NAT64. We unwrap them and validate the embedded IPv4.
_NAT64_PREFIX = ipaddress.IPv6Network("64:ff9b::/96")
# IPv4-mapped IPv6: ::ffff:0:0/96
_IPV4_MAPPED_PREFIX = ipaddress.IPv6Network("::ffff:0:0/96")


def _unwrap_ipv6(ip_obj: ipaddress.IPv6Address) -> Optional[ipaddress.IPv4Address]:
    """
    If the IPv6 address is NAT64 (64:ff9b::/96) or IPv4-mapped (::ffff:x.x.x.x),
    extract and return the embedded IPv4 address. Otherwise return None.
    """
    if ip_obj in _NAT64_PREFIX or ip_obj in _IPV4_MAPPED_PREFIX:
        # Last 32 bits hold the IPv4
        ipv4_int = int(ip_obj) & 0xFFFFFFFF
        return ipaddress.IPv4Address(ipv4_int)
    return None


def _is_ip_restricted(ip_obj: Union[ipaddress.IPv4Address, ipaddress.IPv6Address]) -> bool:
    """
    Returns True if the IP should be blocked for SSRF reasons.
    Handles NAT64/IPv4-mapped unwrapping transparently.
    """
    if isinstance(ip_obj, ipaddress.IPv6Address):
        unwrapped = _unwrap_ipv6(ip_obj)
        if unwrapped is not None:
            # Validate the embedded IPv4 instead of the NAT64 wrapper
            return _is_ip_restricted(unwrapped)

    return (
        ip_obj.is_private
        or ip_obj.is_loopback
        or ip_obj.is_link_local
        or ip_obj.is_multicast
        or ip_obj.is_reserved
        or ip_obj.is_unspecified
    )


def is_safe_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validates a URL against SSRF attacks:
    - Only http/https allowed
    - Hostname must resolve to a valid public IP
    - Private, loopback, link-local, multicast, and cloud metadata IPs are blocked.
    - NAT64-mapped (64:ff9b::/96) and IPv4-mapped (::ffff:/96) IPv6 addresses are
      unwrapped to their embedded IPv4 before checking, preventing false positives
      on legitimate public hosts resolved via IPv6 NAT64.
    """
    if not url or not isinstance(url, str):
        return False, "Empty or invalid URL"

    url = url.strip()
    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"URL parse error: {str(e)}"

    if parsed.scheme.lower() not in ("http", "https"):
        return False, f"Disallowed scheme: {parsed.scheme} (only http/https allowed)"

    hostname = parsed.hostname
    if not hostname:
        return False, "Missing hostname"

    hostname_lower = hostname.lower()
    if hostname_lower in BLOCKED_HOSTNAMES or hostname_lower.endswith(".local") or hostname_lower.endswith(".internal"):
        return False, f"Forbidden hostname: {hostname}"

    # Resolve hostname to IP(s) and check each one
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        if not addr_info:
            return False, f"Could not resolve host: {hostname}"

        for family, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            try:
                ip_obj = ipaddress.ip_address(ip_str)
            except ValueError:
                continue

            if _is_ip_restricted(ip_obj):
                # Build a helpful display string
                display = ip_str
                if isinstance(ip_obj, ipaddress.IPv6Address):
                    unwrapped = _unwrap_ipv6(ip_obj)
                    if unwrapped:
                        display = f"{ip_str} (embedded IPv4: {unwrapped})"
                return False, f"Target IP {display} is in a restricted range (private/internal/cloud-metadata)"

    except socket.gaierror:
        return False, f"Host DNS resolution failed for {hostname}"
    except Exception as e:
        return False, f"IP validation error: {str(e)}"

    return True, None
