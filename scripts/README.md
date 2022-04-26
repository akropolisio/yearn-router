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
 - `"create_call"` - the CreateCall contract to deploy contracts via Gnosis Safe. You can find an address for required network in [safe-deployments](https://github.com/gnosis/safe-deployments) repo
 - `"gnosis_safe"` - Gnosis Safe account, make sure its network matches the `{chain.id}`
 - `"vault_registry"` - the address resolved for `v2.registry.ychad.eth`

For the first deployment `"proxy_admin"`, `"proxy"`, `"implementation"` addresses should be empty. They will be set later after deploying the corresponding contracts.

## Scripts

### deploy/0_deploy_admin.py

Deploys ProxyAdmin and transfers ownership to the Gnosis Safe account.

1. run script:
  ```bash
  brownie run 0_deploy_admin --network mainnet
  ```
2. check that the contract address has been saved in `addresses/{chain.id}.json`.

### deploy/1_deploy_implementation.py

Creates transaction in Gnosis Safe to deploy YearnRouter.
1. run script:
  ```bash
  brownie run 1_deploy_implementation --network mainnet-fork
  ```

### deploy/2_deploy_proxy.py

Creates transaction in Gnosis Safe to deploy proxy.

1. wait for the transaction created in the previous script to complete. Open the transaction on Etherscan and copy the deployed contract address from the logs.
2. run script:
  ```bash
  brownie run 2_deploy_proxy --network mainnet-fork
  ```
3. you will be prompted to enter the YearnRouter address. Paste the copied address to the console.
4. when the script completes, check that the YearnRouter address has been saved in `addresses/{chain.id}.json`.

### deploy/3_verify_contracts.py

Tries to verify contracts, displays instructions for manual verification if automatic verification is not available.

1. wait for the transaction created in the previous script to complete. Open the transaction on Etherscan and copy the deployed contract address from the logs.
2. run script:
  ```bash
  brownie run 3_verify_contracts --network mainnet
  ```
3. you will be prompted to enter the proxy address. Paste the copied address to the console.
4. when the script completes, check that the proxy address has been saved in `addresses/{chain.id}.json`.

### deploy/4_initialize_contracts.py

Creates transaction in Gnosis Safe to initialize both the original and the proxied YearnRouter contracts.

1. run script:
  ```bash
  brownie run 4_initialize_contracts --network mainnet-fork
  ```
