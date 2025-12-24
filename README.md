# Country IP CIDR Aggregator
A lightweight Python script to fetch, parse, and aggregate IPv4 and IPv6 subnets for specific countries directly from Regional Internet Registries (RIR).

## Features
- **RIR Data Source**: Fetches the latest delegated statistics from all five RIRs: RIPE, ARIN, APNIC, LACNIC, and AFRINIC.
- **Aggregation**: Automatically merges adjacent subnets and removes nested networks (supernetting) using the ipaddress library to minimize the output size.
- **Flexible Input**: Supports fetching a single country or a batch list of countries.
- **Dual Stack**: Processes both IPv4 and IPv6 ranges.
- **Zero Dependencies**: Runs on standard Python 3 libraries.

## Requirements
Python 3.3+

## Installation
``` bash
clone the repository:Bashgit clone https://github.com/yourusername/country-ip-aggregator.git
cd country-ip-aggregator
```

## Usage
### 1. Fetch IPs for a Single Country
Use the `-c` flag with the ISO 3166-1 alpha-2 country code.
```bash
# fetch all IP ranges for Russia and save to ru_subnets.txt
python3 main.py -c RU -o ru_subnets.txt
```


### 2. Fetch IPs for Multiple Countries
Create a text file containing country codes (one per line), then use the `-l` flag.
#### countries.txt:
```Plaintext
UA
PL
DE
```

#### Command:
```Bash
python3 main.py -l countries.txt -o europe_subnets.txt
```

## CLI Arguments
### CLI Arguments

| Short | Long Option | Required | Description |
|:---:|:---|:---:|:---|
| `-c` | `--country` | No* | Target country code (ISO 3166-1 alpha-2), e.g., `UA`, `US`. |
| `-l` | `--list` | No* | Path to a text file containing a list of country codes. |
| `-o` | `--output` | **Yes** | Path to the output file where IP ranges will be saved. |
| `-h` | `--help` | No | Show the help message and exit. |

> **Note:** You must provide either `-c` or `-l` to specify the target countries.

## How It Works
1. Download: The script downloads delegated-*-latest files from official RIR FTP servers
2. Filter: It iterates through the data, filtering by the requested Country Code (CC) and status (allocated or assigned).
3. Convert:
    - IPv4: Converts the "number of hosts" value into a CIDR prefix (e.g., 1024 hosts $\rightarrow$ /22).
    - IPv6: Reads the prefix length directly.
4. Aggregate: Uses ipaddress.collapse_addresses() to merge contiguous ranges (e.g., 10.0.0.0/24 + 10.0.1.0/24 $\rightarrow$ 10.0.0.0/23).
5. Output: Writes the optimized list to the specified file.
6. Done!

## License
Distributed under the MIT License. See [LICENSE](LICENSE) for more information.