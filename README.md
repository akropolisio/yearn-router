# yearn-router

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

#### Local

- you will need Python 3.8 and Node.js >=14.x
- install dependencies:
  ```bash
  make clean && make install-all
  ```

### Setup .env

- run `cp .example.env .env`
- insert keys into `.env`

### Run tests

- to run tests, "-s" will provide print outputs which this test suite uses to visualize yield:
  ```bash
  brownie test -s
  ```
