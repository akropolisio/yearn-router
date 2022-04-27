from brownie import UtilProxy, YearnRouter
from brownie.exceptions import ContractExists
from brownie.network.contract import ProjectContract
from brownie.project.main import Project, get_loaded_projects


def get_proxied_router(address) -> YearnRouter:
    proxy = UtilProxy.at(address)
    impl_proxy: YearnRouter
    try:
        impl_proxy = YearnRouter.at(proxy.address)
    except ContractExists:
        project: Project = get_loaded_projects()[0]
        impl_proxy = ProjectContract(
            project,
            build={
                "abi": YearnRouter.abi,
                "contractName": "YearnRouter"
            }, address=proxy.address)
    return impl_proxy
