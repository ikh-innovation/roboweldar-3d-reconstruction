import os
from typing import List, Dict

import pyfiware
import simplejson as json
import datetime as dt

from config import ROOT_DIR

# TODO: Test communication with Orion
# TODO: Integrate context updates into entrypoint's while loop

def create_entity(oc: pyfiware.OrionConnector, entity_id: str, element_type: str, data: Dict):
    try:
        print("Deleting entity...")
        oc.delete(entity_id=entity_id)
    except pyfiware.FiException as err:
        print(err.message)

    device = oc.get(entity_id=entity_id)
    if not device:
        oc.create(element_id=entity_id, element_type=element_type,
                  attributes=data)


def post_entity_context_update(oc: pyfiware.OrionConnector, entity_id: str, element_type: str, data: Dict):
    device = oc.get(entity_id=entity_id)
    if device:
        oc.patch(element_id=entity_id, element_type=element_type,
                 attributes=data)

        device = oc.get(entity_id=entity_id)
        print(device)


def example():
    oc: pyfiware.OrionConnector = pyfiware.OrionConnector(host="127.0.0.1:1026")

    entity_id: str = "3DRecService"
    element_type: str = "ComputationService"

    data: Dict = json.loads(os.path.join(ROOT_DIR, "data_model", "example1.json"))

    create_entity(oc, entity_id, element_type, data)
    post_entity_context_update(oc, entity_id, data)


if __name__ == '__main__':
    # first run ../test/run.sh to get the Orion server up and running

    example()
