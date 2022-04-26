.ONESHELL:

install-all:
	npm install -g ganache-cli@6.12.2
	pip install -r requirements/requirements.txt
	$(MAKE) install-contracts-deps
	yarn
	brownie networks import ./network-config.yml False

install-contracts-deps:
	brownie pm install "OpenZeppelin/openzeppelin-contracts@4.5.0"
	brownie pm install "OpenZeppelin/openzeppelin-contracts-upgradeable@4.5.2"
	brownie pm install "yearn/yearn-vaults@0.4.3"
	brownie pm clone "OpenZeppelin/openzeppelin-contracts@4.5.0"
	brownie pm clone "OpenZeppelin/openzeppelin-contracts-upgradeable@4.5.2"
	brownie pm clone "yearn/yearn-vaults@0.4.3"

clean:
	rm -rf build OpenZeppelin node_modules yearn