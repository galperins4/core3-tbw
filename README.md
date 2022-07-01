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
cd ~/core3-tbw
# switch to solar branch
git checkout solar
# install and activate virtual environment
python3 -m venv .venv
. .venv/bin/activate
# Workaround for Solar vers > 3.2.0-next.0 setting CPATH 
# causing psycopg2 compilation error for missing header files
if [ -n "$CPATH" ]; then
    SAVEDCPATH=$CPATH
    export CPATH="/usr/include"
fi
# install requirements
pip3 install -r requirements.txt
# deactivate virtual environment
deactivate
if [ -n "$SAVEDCPATH" ]; then
    export CPATH=$SAVEDCPATH
fi

# clone config example
cp ~/core3-tbw/core/config/config.ini.example ~/core3-tbw/core/config/config.ini
# fill out config (see below)
nano ~/core3-tbw/core/config/config.ini

# if you will run a pool; clone pool config example
cp ~/core3-tbw/core/config/pool_config.ini.example ~/core3-tbw/core/config/pool_config.ini
# fill out config (see below)
nano ~/core3-tbw/core/config/pool_config.ini

# run script with pm2
cd ~/core3-tbw/core
# if you will run the pool along;
pm2 start apps.json
# if you will not run the pool;
pm2 start apps.json --only tbw
pm2 start apps.json --only pay
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
| passphrase | passphrase | 12 word delegate passphrase |
| secondphrase | None | Second 12 word delegate passphrase |
| delegate_fee | 25,25 | These are the percentages for delegates to keep and distribute among x accounts (Note: first entry is reserve account and is required! All others are optional |
| delegate_fee_address | addr1,addr2 | These are the addresses to go with the delegate feeskeep percentages (Note: first entry is reserve account and is required! All others are optional |

**NOTE 1**: When TBW is catching up with a large number of forged blocks, you may receive 429 rate limit rejects from the core API for dynamic-fee requests causing payment transaction fees reverting to the default value of 0.1 SXP. To prevent this, you can add localhost to API RATE WHITELIST in core environment configuration:
```
nano ~/.config/solar-core/testnet/.env
...
...
CORE_API_RATE_LIMIT_WHITELIST=127.0.0.1
```
> make sure CORE_API_TRUST_PROXY is not enabled

Next restart core
```
pm2 restart <solar-relay-process-id> --update-env
pm2 restart <solar-forger-process-id> --update-env
```

Should you receive an error and core stops after this; that means your installation needs a bugfix:
```
nano ~/.solarrc
...
...
# replace alias pm2="/home/solar/.solar/.pnpm/bin/pm2" with the following
alias pm2="bash --rcfile /home/solar/.solar/.env -i /home/solar/.solar/.pnpm/bin/pm2 $@"
...
...
```
log out, log back in and restart the core (and forger as necessary)
```
pm2 restart <solar-relay-process-id> --update-env
pm2 restart <solar-forger-process-id> --update-env
```

### [Exchange] (Experimental - Ark network only)
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

**NOTE 3**: exchange_configtest.py (under core folder) has been created to test exchange config to prior to turning on. To execute run `python3 test_exchange.py` after setting up configuration as described in the table above

### [Other] 
| Option | Default Setting | Description | 
| :--- | :---: | :--- |
| custom | N | Changing value to Y will enable the script to set custom share rates. Run ```python3 tbw.py``` and you will be prompted to enter a voter address and share rate to update. Note - this change only affects a single voter |
| manual_pay | N | Changing value to Y will enable the script to run a manual pay run outside of the normal interval. Run ```python3 tbw.py``` which will force unpaid rewards to stage for a payrun.  |
| update_share | N | Changing value to Y will enable the ability to update voter share rate in database |

**NOTE 1**: Each of these settings should be reset to N in the config after running the script with the specific option enabled

### [Logging]
| Option | Default Setting | Description | 
| :--- | :---: | :--- |
| loglevel | INFO | Can be turned to DEBUG in order to have full debug outputs |
| formatter | %(levelname)s %(message)s | Log formatter |

### [Donate]
| Option | Default Setting | Description | 
| :--- | :---: | :--- |
| donate | N | Changing value to Y will enable donations to a specified address |
| donate_address | addr1 | This is the donation address. If you like my work, please consider adding a donation to your payment runs. Please contact Delegate Goose on Discord/Telegram for an address |
| donate_percent | 0 | This is the donation percentage. The value is a percent of the reserve account rewards. For example, if the current payment run has 2 Ark rewards in the reserve account and this is set at 10 (percent), the donation will be 0.2 Ark and the new reserve account payment will be reduced to 1.8 Ark |

## Config options for pool 
### [pool]
| Option | Default Setting | Description | 
| :--- | :---: | :--- |
| pool_ip | xx.xx.xx.xx | IP of the node the pool is installed on |
| pool_port | 5000 | Port for pool |
| pool_template | osrn | Set the pool website template - only option currently |
| explorer | https://testnet.explore.solar | The address of the explorer for the coin. |
| coin | DSXP | Coin |
| proposal1 | https://delegates.solar.org/delegates/xxxx | Link to delegate proposal |
| proposal2 | https://yy.yy.yy | Link to the delegate proposal in different language |
| proposal2_lang | CC | Language (code) of the second proposal |


## To Do

- TBD

## Changelog


### 1.1.0
- upgrade script for new vote transaction
- upgrade script for transfer / multipayment transaction type merge

### 1.0.2
- bug fix - temporary code to account for dev_fund if delegate is a voter

### 0.1
- initial release

## Security

If you discover a security vulnerability within this package, please open an issue. All security vulnerabilities will be promptly addressed.

## Credits

- [galperins4](https://github.com/galperins4)
- [All Contributors](../../contributors)

## License

[MIT](LICENSE) © [galperins4](https://github.com/galperins4)
