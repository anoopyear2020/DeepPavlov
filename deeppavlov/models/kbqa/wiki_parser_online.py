# Copyright 2017 Neural Networks and Deep Learning lab, MIPT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from logging import getLogger
from typing import List, Tuple, Dict

import requests

from deeppavlov.core.common.registry import register

log = getLogger(__name__)


def get_answer(query: str) -> List[Dict[str, Dict[str, str]]]:
    url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql'
    data = []
    for i in range(5):
        try:
            data_0 = requests.get(url, params={'query': query, 'format': 'json'},  timeout=0.5).json()
            if "results" in data_0.keys():
                data = data_0['results']['bindings']
            elif "boolean" in data_0.keys():
                data = data_0['boolean']
            break
        except:
            pass

    return data


@register('wiki_parser_online')
class WikiParserOnline:
    """This class extract relations or labels from Wikidata query service"""

    def __init__(self, **kwargs) -> None:
        pass

    def find_label(self, entity: str) -> str:
        entity = str(entity).replace('"', '')
        if entity.startswith("http://www.wikidata.org/entity/Q"):
            entity = entity.split('/')[-1]
        if entity.startswith("Q"):
            query = f"SELECT DISTINCT ?label WHERE {{ wd:{entity} rdfs:label ?label . FILTER (lang(?label) = 'en') }}"
            labels = get_answer(query)
            if labels:
                labels = [label["label"]["value"] for label in labels]
                return labels[0]
        elif entity.endswith("T00:00:00Z"):
            return entity.split('T00:00:00Z')[0]
        else:
            return entity

    def find_rels(self, entity: str, direction: str, rel_type: str = None) -> List[str]:
        if direction == "forw":
            query = f"SELECT DISTINCT ?rel WHERE {{ wd:{entity} ?rel ?obj . }}"
        else:
            query = f"SELECT DISTINCT ?rel WHERE {{ ?subj ?rel wd:{entity} . }}"
        rels = get_answer(query)
        if rels:
            rels = [rel["rel"]["value"] for rel in rels]

        if rel_type is not None:
            start_str = f"http://www.wikidata.org/prop/{rel_type}"
        else:
            start_str = "http://www.wikidata.org/prop/P"
        rels = [rel for rel in rels if rel.startswith(start_str)]
        return rels