import os
from copy import deepcopy
from typing import List, Dict

import pyfiware
import simplejson as json
import datetime as dt

from config import ROOT_DIR


# TODO: Test communication with Orion
# TODO: Integrate context updates into entrypoint's while loop

def create_entity(oc: pyfiware.OrionConnector, entity_id: str, element_type: str, data: Dict):
    try:
        print("Deleting entity with id: {}".format(entity_id))
        oc.delete(entity_id=entity_id)
    except pyfiware.FiException as err:
        print("Entity with id {} does not exist.".format(entity_id))
        print(err.message)

    print("Creating entity with id: {}".format(entity_id))

    oc.create(element_id=entity_id, element_type=element_type,
              attributes=data)


def post_entity_context_update(oc: pyfiware.OrionConnector, entity_id: str, element_type: str, data: Dict):
    device = oc.get(entity_id=entity_id)
    if device:
        oc.patch(element_id=entity_id, element_type=element_type,
                 attributes={'type': 'StructuredValue',
                             'value': data, "metadata": {}})

        device = oc.get(entity_id=entity_id)
        print(device)


def example():
    oc: pyfiware.OrionConnector = pyfiware.OrionConnector(host="127.0.0.1:1026")

    entity_id: str = "3DRecService"
    element_type: str = "ComputationService"
    with open(os.path.join(ROOT_DIR, "data_model", "computation_service", "example1.json"), "r") as infile:
        data: Dict = json.load(infile)

    data_modified = deepcopy(data)
    data_modified.pop("id", None)
    data_modified.pop("type", None)

    create_entity(oc, entity_id, element_type, data_modified)
    post_entity_context_update(oc, entity_id, element_type, data_modified)


if __name__ == '__main__':
    # first run ../test/run.sh to get the Orion server up and running

    example()
