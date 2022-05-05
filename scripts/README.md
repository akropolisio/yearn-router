# Deployment instructions
## Add deployer account to brownie

- Import a private key
  ```bash
  $ brownie accounts new deployer
  ```
- Or import a .json keystore
  ```bash
  $ brownie accounts import deployer keystore.json
  ```

## Fill in contract addresses in `addresses/{chain.id}.json`
If `addresses/{chain.id}.json` doesn't include the following addresses, fill them in:
 - `"gnosis_safe"` - Gnosis Safe account, make sure its network matches the `{chain.id}`. It will be the owner of ProxyAdmin and Proxy implementation contracts.
 - `"vault_registry"` - the address resolved for `v2.registry.ychad.eth`

For the first deployment `"proxy_admin"`, `"proxy"`, `"implementations"` addresses should be empty. They will be set later after deploying the corresponding contracts.

## Scripts

### deploy/0_deploy_admin.py

Deploys ProxyAdmin and transfers ownership to the Gnosis Safe account.

1. run script:
  ```bash
  brownie run 0_deploy_admin --network mainnet
  ```
2. check that the contract address has been saved in `addresses/{chain.id}.json`.

### deploy/1_deploy_implementation.py

Deploys YearnRouter.
1. run script:
  ```bash
  brownie run 1_deploy_implementation --network mainnet
  ```
2. check that the contract address has been saved in `addresses/{chain.id}.json`.

### deploy/2_deploy_proxy.py

Deploys Proxy with implementation and admin addresses from `addresses/{chain.id}.json`, and initializes proxy implementation

1. run script:
  ```bash
  brownie run 2_deploy_proxy --network mainnet
  ```
2. check that the contract address has been saved in `addresses/{chain.id}.json`.

# Upgrading proxy implementation
Proxy and ProxyAdmin contracts should be deployed only once. The instructions below show how to deploy a new version of implementation contract and apply changes to the Proxy contract.
1. make necessary changes in `YearnRouter.sol` contract considering [the proxy pattern caveats](https://docs.openzeppelin.com/upgrades-plugins/1.x/proxies#summary).
2. run script:
  ```
    brownie run 1_deploy_implementation --network mainnet
  ```
3. use the deployed contract address to create an `upgrade` transaction on `proxy_admin` contract in Gnosis Safe app.