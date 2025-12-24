import urllib.request
import math
import ipaddress
import argparse
import sys
import os

RIR_URLS = [
    "https://ftp.ripe.net/ripe/stats/delegated-ripencc-latest",
    "https://ftp.arin.net/pub/stats/arin/delegated-arin-latest",
    "https://ftp.apnic.net/pub/stats/apnic/delegated-apnic-latest",
    "https://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-latest",
    "https://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-latest"
]


def parse_arguments():
    parser = argparse.ArgumentParser(description="RIR Statistics Parser & Aggregator")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', '--country', type=str, help="Single country code (ISO 3166-1 alpha-2), e.g., RU")
    group.add_argument('-l', '--list', type=str, help="Path to file containing list of country codes")

    parser.add_argument('-o', '--output', type=str, required=True, help="Path to output file")

    return parser.parse_args()


def get_target_countries(args):
    countries = set()

    if args.country:
        countries.add(args.country.strip().upper())

    elif args.list:
        if not os.path.exists(args.list):
            print(f"Error: File {args.list} not found.")
            sys.exit(1)

        with open(args.list, 'r') as f:
            for line in f:
                code = line.strip().upper()
                # Фильтрация валидных 2-буквенных кодов
                if len(code) == 2 and code.isalpha():
                    countries.add(code)

    print(f"Target countries: {', '.join(countries)}")
    return countries


def fetch_and_aggregate(countries):
    ipv4_nets = []
    ipv6_nets = []

    print("Fetching data from RIRs...")

    for url in RIR_URLS:
        try:
            print(f"  Processing: {url}")
            with urllib.request.urlopen(url, timeout=30) as response:
                for line in response:
                    line = line.decode('utf-8').strip()
                    if line.startswith('#') or not line:
                        continue

                    parts = line.split('|')
                    if len(parts) < 7:
                        continue

                    cc = parts[1].upper()
                    ip_type = parts[2]
                    start_ip = parts[3]
                    value = parts[4]
                    status = parts[6]

                    if cc in countries and status in ['ipv4', 'ipv6', 'allocated', 'assigned']:
                        cidr_str = ""
                        try:
                            if ip_type == 'ipv4':
                                host_count = int(value)
                                prefix = 32 - int(math.log(host_count, 2))
                                cidr_str = f"{start_ip}/{prefix}"
                            elif ip_type == 'ipv6':
                                cidr_str = f"{start_ip}/{value}"

                            if cidr_str:
                                net = ipaddress.ip_network(cidr_str, strict=False)
                                if net.version == 4:
                                    ipv4_nets.append(net)
                                else:
                                    ipv6_nets.append(net)

                        except (ValueError, IndexError, ipaddress.AddressValueError):
                            continue

        except Exception as e:
            print(f"  Error processing {url}: {e}")

    print(f"Raw count: {len(ipv4_nets)} IPv4, {len(ipv6_nets)} IPv6")
    return ipv4_nets, ipv6_nets


def save_aggregated(ipv4_nets, ipv6_nets, output_file):
    print("Aggregating subnets...")

    ipv4_aggr = ipaddress.collapse_addresses(ipv4_nets)
    ipv6_aggr = ipaddress.collapse_addresses(ipv6_nets)

    count = 0
    with open(output_file, 'w') as f:
        for net in ipv4_aggr:
            f.write(f"{str(net)}\n")
            count += 1
        for net in ipv6_aggr:
            f.write(f"{str(net)}\n")
            count += 1

    print(f"Successfully saved {count} aggregated subnets to {output_file}")


def main():
    args = parse_arguments()
    countries = get_target_countries(args)

    if not countries:
        print("No valid country codes found.")
        sys.exit(1)

    v4, v6 = fetch_and_aggregate(countries)
    save_aggregated(v4, v6, args.output)


if __name__ == "__main__":
    main()