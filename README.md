# Python True Block Weight - Core 3

## Prerequisites

1. Install pip and python3.6 or above

2. Install `pm2`

```bash
npm install pm2@latest -g
# or
yarn global add pm2
```

## Clean / New Installation

```sh
# Install and sync relay server
# clone repository
git clone https://github.com/galperins4/core3-tbw
# install requirements
cd ~/core3-tbw
pip3 install -r requirements.txt
# fill out config (see below)
nano ~/core3-tbw/core/config/config.ini
# initialize
cd ~/core3-tbw/core
python3 tbw.py
# run script with pm2
pm2 start apps.json
```

## Configuration & Usage

1. After the repository has been cloned you need to open the [config](./core/config/config.ini) and change it to your liking (see [Available Configuration Options](#available-configuration-options))

Main values to update here are the following sections of the config file:

```txt
[static]
[delegate]
[payment]
[exchange]
[other]
[donate]
```


Python 3.6+ is required.

## Available Configuration Options 
### [Static]
| Option | Default Setting | Description | 
| :--- | :---: | :--- |
| atomic | 100000000 | atomic value - do not change |
| network | ark_devnet | ark_mainnet or persona_mainnet or qredit_mainnet etc.. |
| username | username | This is the postgresql database username (usually your os username) |
| start_block | 0 | Script will start calculations only for blocks after specified start block |

### [Delegate]
| Option | Default Setting | Description | 
| :--- | :---: | :--- |
| delegate | delegate | Delegate name |
| message | message | ARK and ARK Fork coins only - message you want in vendor field for share payments |
| voter_share | 50  | Percentage to share with voters |
| vote_cap| 0 | Cap voters for how much they can earn with votes. For example 10000 will mean any wallet over 10K will only be paid based on 10K weight |
| vote_min | 0 | Use this if you have a minimum wallet balance to be eligible for payments |
| whitelist | N | Enable payment to only whitelisted addresses |
| whitelist_addr | addr1,addr2,addr3 | Comma seperated list of addresses to allow voter payments to only whitelisted addresses |
| blacklist | N | Enable blocking of payments to specific addresses |
| blacklist_addr | addr1,addr2,addr3 | Comma seperated list of addresses to block from voter payments |

### [Payment]
| Option | Default Setting | Description | 
| :--- | :---: | :--- |
| interval | 211  | The interval you want to pay voters in blocks. A setting of 211 would pay ever 211 blocks (or 422 ark) |
| multi | N | Change to "Y" if you'd like payments to be made using Multipayments |
| multi_fee | 0.1 | Experimental setting to adjust default Multipayments fee |
| passphrase | passphrase | 12 word delegate passphrase |
| secondphrase | None | Second 12 word delegate passphrase |
| delegate_fee | 25,25 | These are the percentages for delegates to keep and distribute among x accounts (Note: first entry is reserve account and is required! All others are optional |
| delegate_fee_address | addr1,addr2 | These are the addresses to go with the delegate feeskeep percentages (Note: first entry is reserve account and is required! All others are optional |


### Exchange (Experimental - Ark network only)
| Option | Default Setting | Description | 
| :--- | :---: | :--- |
| exchange | N | Changing value to Y will enable exchange swap functionality |
| convert_from | ark, ark | Network the swap is sending from - ark only |
| convert_address | addr1,addr2 | Reward address we are converting from for the swap - can support one or many|
| convert_to | usdc,xrp | Cryptocurrency we want to swap / exchange into - can support one or many |
| address_to | usdc_addr1,xrp_addr2 | Addresses to exchange into - can support one or many |
| network_to | eth,xrp | Network for the receving swap cryptocurrency - can support one or many |
| provider | provider,provider | Provider of the swap - Available options are "SimpleSwap" or "ChangeNow" |

**NOTE 1**: Exchange address does not currently work with fixed amount/address processing. Do NOT enable exchange for fixed accounts

**NOTE 2**: For full disclosure - swap exchanges require an API key to create. All swaps are requested through my affiliate accounts at SimpleSwap / ChangeNow which generates a referral fee. All exchange/swap processing is the responsibility of SimpleSwap and ChangeNow.

**NOTE 3**: exchange_configtest.py (under core folder) has been created to test exchange config to prior to turning on. To execute run `python3 exchange_configtest.py` after setting up configuration as described in the table above


### Pool
| Config Option | Default Setting | Description | 
| :--- | :---: | :--- |
| POOL_IP | xx.xx.xx.xx | IP of the node the pool is installed on |
| EXPLORER | https://dexplorer.ark.io/ | The address of the explorer for the coin |
| COIN | DARK | Coin name, DARK, ARK, QREDIT, PRSN etc |
| PROPOSAL | https://xx.xx.xx/ | Link to delegate proposal (if any) |
| POOL_PORT | 5000 | Port for pool/webhooks |
| CUSTOM_PORT | 5004 | Custom port for using custom voter share update functionality |
| POOL_VERSION | original | Set the pool website version - options are "original" or "geops" |

## To Do

- TBD

## Changelog

### 0.1
- initial release

## Security

If you discover a security vulnerability within this package, please open an issue. All security vulnerabilities will be promptly addressed.

## Credits

- [galperins4](https://github.com/galperins4)
- [All Contributors](../../contributors)

## License

[MIT](LICENSE) © [galperins4](https://github.com/galperins4)
