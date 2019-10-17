import os
import csv
from pathlib import Path
from .cpo_statuses import in_process_states, final_states
from .legislation import legislation  # noqa

cpo_statuses = {
    "in_process_states": in_process_states,
    "final_states": final_states
}

data_dir = Path(os.path.dirname(__file__))
local_authority_csv = 'local-authority-eng.csv'
cvs_file_path = os.path.join(data_dir, local_authority_csv)


class LocalAuthorityMapping:

    def __init__(self):
        self.local_authority_mapping = {}
        with open(cvs_file_path, 'r') as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                key = f"local-authority-eng:{row['local-authority-eng']}"
                self.local_authority_mapping[key] = row['official-name']

        self.local_authority_mapping['national-park:1'] = 'Peak District National Park'
        self.local_authority_mapping['national-park:2'] = 'Lake District National Park'
        self.local_authority_mapping['national-park:3'] = 'Dartmoor National Park'
        self.local_authority_mapping['national-park:4'] = 'North York Moors National Park'
        self.local_authority_mapping['national-park:5'] = 'Yorkshire Dales National Park'
        self.local_authority_mapping['national-park:6'] = 'Exmoor National Park'
        self.local_authority_mapping['national-park:7'] = 'Northumberland National Park'
        self.local_authority_mapping['national-park:8'] = 'Broads Authority'
        self.local_authority_mapping['national-park:9'] = 'New Forest National Park'
        self.local_authority_mapping['national-park:10'] = 'South Downs National Park'

    def get_local_authority_name(self, local_authority_id):
        return self.local_authority_mapping.get(local_authority_id)

    def order_by_name(self):
        sorted_mapping = sorted(self.local_authority_mapping.items(), key=lambda kv: kv[1])
        return sorted_mapping
