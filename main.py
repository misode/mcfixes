
# MIT License
# 
# Copyright (c) 2022 Misode
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import json
import click
import requests
import urllib.parse

MCMETA = 'https://raw.githubusercontent.com/misode/mcmeta'
MOJIRA = 'https://bugs.mojang.com/rest/api/2'

@click.command()
def main():
	versions = requests.get(f'{MCMETA}/summary/versions/data.min.json').json()
	os.makedirs('versions', exist_ok=True)
	name_prefix = ''
	for v in versions:
		if v['name'] == '1.14.4 Pre-Release 6':
			name_prefix = 'Minecraft '
		process(v, name_prefix)


def process(version, name_prefix):
	name = name_prefix + version['name'].replace('Snapshot ', '')
	jql = urllib.parse.quote(f'project=MC AND resolution=Fixed AND fixVersion="{name}"', safe='')
	result = requests.get(f'{MOJIRA}/search?maxResults=1000&jql={jql}').json()
	issues = [map_issue(i) for i in result['issues']]
	with open(f'./versions/{version["id"]}.json', 'w') as f:
		json.dump(issues, f, indent='  ')
		f.write('\n')


def map_issue(issue):
	categories = issue['fields']['customfield_11901']
	priority = issue['fields']['customfield_12200']
	return {
		'id': issue['key'],
		'summary': issue['fields']['summary'],
		'labels': issue['fields']['labels'],
		'status': issue['fields']['status']['name'],
		'confirmation_status': issue['fields']['customfield_10500']['value'],
		'categories': [c['value'] for c in (categories if categories else [])],
		'priority': priority['value'] if priority else 'None',
		'fix_versions': [v['name'] for v in issue['fields']['fixVersions']],
		'creation_date': issue['fields']['created'],
		'resolution_date': issue['fields']['resolutiondate'],
		'updated_date': issue['fields']['updated'],
		'watches': issue['fields']['watches']['watchCount'],
		'votes': issue['fields']['votes']['votes'],
	}


if __name__ == '__main__':
	main()
