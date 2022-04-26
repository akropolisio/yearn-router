import json
import shutil


def publish_sources(contract, address):
    info = contract.get_verification_info()

    try:
        contract.publish_source(contract.at(address))
    except:
        print(
            f"\nUnable to verify {info['contract_name']}! Use the 'verification_sources/{info['contract_name']}' folder to verify manually"
        )

        prepare_verification_sources(contract)
        print_verification_info(contract, address)


def print_verification_info(contract, address):
    info = contract.get_verification_info()
    print(f"\n***** {info['contract_name']} *****")
    print(f"Address: {address}")
    print(f"Compiler Version: {info['compiler_version']}")
    print(f"License Type: {info['license_identifier']}")
    print(f"Optimizer Enabled: {info['optimizer_enabled']}")


def prepare_verification_sources(contract):
    output_path = get_output_path(contract)
    clean_folder(output_path)

    info = contract.get_verification_info()

    with open(f"{output_path}.json", "x", encoding="utf-8") as file:
        file.write(json.dumps(info["standard_json_input"]))


def clean_folder(path):
    try:
        shutil.rmtree(path)
    except:
        pass


def get_output_path(contract):
    info = contract.get_verification_info()
    return f"verification_sources/{info['contract_name']}"
