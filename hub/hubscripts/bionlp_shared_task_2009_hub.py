# coding=utf-8
# Copyright 2022 The HuggingFace Datasets Authors and
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


from pathlib import Path
from typing import Dict, List

import datasets

from .bigbiohub import kb_features
from .bigbiohub import BigBioConfig
from .bigbiohub import Tasks

_LANGUAGES = ['English']
_PUBMED = True
_LOCAL = False
_CITATION = """\
@inproceedings{kim-etal-2009-overview,
    title = "Overview of {B}io{NLP}{'}09 Shared Task on Event Extraction",
    author = "Kim, Jin-Dong  and
      Ohta, Tomoko  and
      Pyysalo, Sampo  and
      Kano, Yoshinobu  and
      Tsujii, Jun{'}ichi",
    booktitle = "Proceedings of the {B}io{NLP} 2009 Workshop Companion Volume for Shared Task",
    month = jun,
    year = "2009",
    address = "Boulder, Colorado",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/W09-1401",
    pages = "1--9",
}
"""

_DATASETNAME = "bionlp_shared_task_2009"
_DISPLAYNAME = "BioNLP 2009"

_DESCRIPTION = """\
The BioNLP Shared Task 2009 was organized by GENIA Project and its corpora were curated based
on the annotations of the publicly available GENIA Event corpus and an unreleased (blind) section
of the GENIA Event corpus annotations, used for evaluation.
"""

_HOMEPAGE = "http://www.geniaproject.org/shared-tasks/bionlp-shared-task-2009"

_LICENSE = 'GENIA Project License for Annotated Corpora'

_URL_BASE = "http://www.nactem.ac.uk/GENIA/current/Shared-tasks/BioNLP-ST-2009/"
_URLS = {
    _DATASETNAME: {
        "train": _URL_BASE + "bionlp09_shared_task_training_data_rev2.tar.gz",
        "test": _URL_BASE
        + "bionlp09_shared_task_test_data_without_gold_annotation.tar.gz",
        "dev": _URL_BASE + "bionlp09_shared_task_development_data_rev1.tar.gz",
    },
}

_SUPPORTED_TASKS = [
    Tasks.NAMED_ENTITY_RECOGNITION,
    Tasks.EVENT_EXTRACTION,
    Tasks.COREFERENCE_RESOLUTION,
]

_SOURCE_VERSION = "1.0.0"

_BIGBIO_VERSION = "1.0.0"

# https://2011.bionlp-st.org/bionlp-shared-task-2011/genia-event-extraction-genia


class BioNLPSharedTask2009(datasets.GeneratorBasedBuilder):
    """TODO: Short description of my dataset."""

    SOURCE_VERSION = datasets.Version(_SOURCE_VERSION)
    BIGBIO_VERSION = datasets.Version(_BIGBIO_VERSION)

    BUILDER_CONFIGS = [
        BigBioConfig(
            name="bionlp_shared_task_2009_source",
            version=SOURCE_VERSION,
            description="bionlp_shared_task_2009 source schema",
            schema="source",
            subset_id="bionlp_shared_task_2009",
        ),
        BigBioConfig(
            name="bionlp_shared_task_2009_bigbio_kb",
            version=BIGBIO_VERSION,
            description="bionlp_shared_task_2009 BigBio schema",
            schema="bigbio_kb",
            subset_id="bionlp_shared_task_2009",
        ),
    ]

    DEFAULT_CONFIG_NAME = "bionlp_shared_task_2009_source"

    _ROLE_MAPPING = {
        "Theme2": "Theme",
        "Theme3": "Theme",
        "Theme4": "Theme",
        "Site2": "Site",
    }

    def _info(self) -> datasets.DatasetInfo:

        if self.config.schema == "source":
            features = datasets.Features(
                {
                    "document_id": datasets.Value("string"),
                    "text": datasets.Value("string"),
                    "text_bound_annotations": [
                        {
                            "id": datasets.Value("string"),
                            "offsets": [[datasets.Value("int64")]],
                            "text": [datasets.Value("string")],
                            "type": datasets.Value("string"),
                        }
                    ],
                    "events": [
                        {
                            "arguments": [
                                {
                                    "ref_id": datasets.Value("string"),
                                    "role": datasets.Value("string"),
                                }
                            ],
                            "id": datasets.Value("string"),
                            "trigger": datasets.Value("string"),
                            "type": datasets.Value("string"),
                        }
                    ],
                    "relations": [
                        {
                            "id": datasets.Value("string"),
                            "type": datasets.Value("string"),
                            "arg1_id": datasets.Value("string"),
                            "arg2_id": datasets.Value("string"),
                            "normalized": [
                                {
                                    "db_name": datasets.Value("string"),
                                    "db_id": datasets.Value("string"),
                                }
                            ],
                        }
                    ],
                    "equivalences": [datasets.Value("string")],
                    "attributes": [datasets.Value("string")],
                    "normalizations": [datasets.Value("string")],
                }
            )

        elif self.config.schema == "bigbio_kb":
            features = kb_features

        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=features,
            homepage=_HOMEPAGE,
            license=str(_LICENSE),
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager) -> List[datasets.SplitGenerator]:
        urls = _URLS[_DATASETNAME]
        data_dir_train = dl_manager.download_and_extract(urls["train"])
        data_dir_test = dl_manager.download_and_extract(urls["test"])
        data_dir_dev = dl_manager.download_and_extract(urls["dev"])

        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={
                    "filepath": data_dir_train,
                    "split": "train",
                },
            ),
            datasets.SplitGenerator(
                name=datasets.Split.TEST,
                gen_kwargs={
                    "filepath": data_dir_test,
                    "split": "test",
                },
            ),
            datasets.SplitGenerator(
                name=datasets.Split.VALIDATION,
                gen_kwargs={
                    "filepath": data_dir_dev,
                    "split": "dev",
                },
            ),
        ]

    def _standardize_arguments_roles(self, kb_example: Dict) -> Dict:

        for event in kb_example["events"]:
            for argument in event["arguments"]:
                role = argument["role"]
                argument["role"] = self._ROLE_MAPPING.get(role, role)

        return kb_example

    def _generate_examples(self, filepath, split):

        filepath = Path(filepath)
        txt_files: List[Path] = [
            file for file in filepath.iterdir() if file.suffix == ".txt"
        ]

        if self.config.schema == "source":
            for i, file in enumerate(txt_files):
                brat_content = parse_brat_file(file)
                yield i, brat_content

        elif self.config.schema == "bigbio_kb":
            for i, file in enumerate(txt_files):
                brat_content = parse_brat_file(file)
                kb_example = brat_parse_to_bigbio_kb(brat_content)
                kb_example = self._standardize_arguments_roles(kb_example)
                kb_example["id"] = kb_example["document_id"]
                yield i, kb_example
