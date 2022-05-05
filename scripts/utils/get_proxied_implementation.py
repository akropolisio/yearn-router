from brownie.exceptions import ContractExists
from brownie.network.contract import ProjectContract
from brownie.project.main import Project, get_loaded_projects


def get_proxied_implementation(ImplContract, proxy_address):
    impl_proxy: ImplContract
    try:
        impl_proxy = ImplContract.at(proxy_address)
    except ContractExists:
        project: Project = get_loaded_projects()[0]
        impl_proxy = ProjectContract(
            project,
            build={
                "abi": ImplContract.abi,
                "contractName": ImplContract.get_verification_info()['contract_name'],
            }, address=proxy_address)
    return impl_proxy
