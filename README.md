# yearn-proxy

A routing contract for Yearn vaults.
For more on this please see [Yearn Documentation](https://docs.yearn.finance/partners/integration_guide#delegated-deposit).

## Development

### Clone repository

- clone using HTTPS
  ```bash
  git clone https://github.com/akropolisio/yearn-proxy.git
  ```
- or SSH
  ```bash
  git@github.com:akropolisio/yearn-proxy.git
  ```
- change directory to yearn-proxy
  ```bash
  cd yearn-proxy
  ```

### Setup environment

#### VSCode + Docker (recommended)

- install [Docker](https://docs.docker.com/get-docker/)
- install [VSCode](https://code.visualstudio.com/)
- install [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) VSCode extension
- open cloned repository in VSCode
- click F1 and run `>Remote-Containers: Reopen in Container`
- wait until all dependencies are installed (you will see the message "Done. Press any key to close the terminal." in the terminal `Configuring`)

#### Manual

- you will need Python 3.8 and Node.js >=14.x
- install ganache-cli
  ```bash
  npm install -g ganache-cli
  ```
- install python requirements
  ```bash
  pip install -r requirements.txt
  ```
- install hardhat (brownie compatible version of hardhat in order to use arbitrum properly)
  ```bash
  sh ./arb-deploy.sh
  ```
- install contracts dependencies
  ```bash
  sh ./security/clone-packages.sh
  ```
- update brownie networks
  ```bash
  brownie networks import network-config.yaml true
  ```

### Setup .env

- run `cp .example.env .env`
- insert keys into `.env`

### Run tests

- to run tests, "-s" will provide print outputs which this test suite uses to visualize yield:
  ```bash
  brownie test -s
  ```
