#!/usr/bin/env python3

import argparse
import yaml

parser = argparse.ArgumentParser(
    description='Copy SRC to DST but modify the services list '
                'of the OpenStackDataPlaneNodeSet so that it '
                'has both the pre-ceph and post-ceph services. ')
parser.add_argument('src', type=str, help='path to source file')
parser.add_argument('dst', type=str, help='path to destination file')

args = parser.parse_args()


def get_pre_ceph_svcs(filename):
    with open(filename, 'r') as f:
        cm = yaml.safe_load(f)
        return cm['data']['nodeset']['services']


def split_sections(filename):
    sections = []
    current_section = []
    with open(filename, 'r') as f:
        for line in f:
            # could not just split on '---' since
            # more yaml is embedded in a var
            if line.startswith('---'):
                if current_section:
                    sections.append(current_section)
                    current_section = []
            else:
                current_section.append(line)

        if current_section:
            sections.append(current_section)
    return sections


pre_ceph_svcs = get_pre_ceph_svcs("edpm-pre-ceph/nodeset/values.yaml")
sections = split_sections(args.src)
with open(args.dst, 'w') as f:
    for section in sections:
        parsed_data = yaml.safe_load(''.join(section))
        if parsed_data['kind'] == 'OpenStackDataPlaneNodeSet':
            parsed_data['spec']['services'] =\
                pre_ceph_svcs + parsed_data['spec']['services']
        f.write('---\n')
        f.write(yaml.safe_dump(parsed_data, indent=2))
