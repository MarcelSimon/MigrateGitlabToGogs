import requests
import json
import subprocess
import os
from IPython.display import display, HTML

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--source_namespace', 
                    help='The namespace in gitlab as it appears in URLs. For example, given the repository address http://mygitlab.com/harry/my-awesome-repo.git, it shows that this repository lies within my personal namespace "harry". Hence I would pass harry as parameter.',
                    required=True)
parser.add_argument('--add_to_private',default=None, action='store_true',help='If you want to add the repositories under your own name, ie. not in any organisation, use this flag.')
parser.add_argument('--add_to_organization',default=None, metavar='organization_name', help='If you want to add all the repositories to an exisiting organisation, please pass the name to this parameter. Organizations correspond to groups in Gitlab. The name can be taken from the URL, for example, if your organization is http://mygogs-repo.com/org/my-awesome-organisation/dashboard then pass my-awesome-organisation here')
parser.add_argument('--source_repo', 
                    help='URL to your gitlab repo in the format http://mygitlab.com/',
                    required=True)
parser.add_argument('--target_repo', 
                    help='URL to your gogs / gitea repo in the format http://mygogs.com/',
                    required=True)
args = parser.parse_args()

assert args.add_to_private or args.add_to_organization is not None, 'Please set either add_to_private or provide a target oranization name!'

print('In the following, we will check out all repositories from ')
print('the namespace %s to the current directory and push it to '%args.source_namespace)
if args.add_to_private:
    print('your personal account', end='')
else:
    print('to the organisation %s'%args.add_to_organization, end='')
print(' as private repositories.')
input('Hit any key to continue!')

gogs_url = args.target_repo + "/api/v1"
gitlab_url = args.source_repo + '/api/v3'

gogs_token = input(("\n\nPlease provide the gogs access token which we use to access \n"
                    "your account. This is NOT your password! Go to \n"
                    "/user/settings/applications\n"
                    "and click on 'Create new token', and copy and paste the \n"
                    "resulting token which is shown afterwards. It should look \n"
                    "like 3240823dfsaefwio328923490832a.\n\ngogs_token=").format(args.target_repo))
assert len(gogs_token)>0, 'The gogs token cannot be empty!'


gitlab_token = input(("\n\nToken to access your GITLAB account. This is NOT your password! Got to \n"
                    "{}/profile/account \n"
                    "and copy the value in section 'Private token'. It should \n"
                    "look like du8dfsJlfEWFJAFhs\n"
                    "\ngitlab_token=").format(args.source_repo))
assert len(gitlab_token)>0, 'The gitlab token cannot be empty!'

#tmp_dir = '/home/simon/tmp/gitlab_gogs_migration'
#print('Using temporary directory %s'%tmp_dir)
## Create temporary directory
#try:
    #os.makedirs(tmp_dir)
    #print('Created temporary directory %s'%tmp_dir)
#except FileExistsError as e:
    #pass
#except Exception as e:
    #raise e

#os.chdir(tmp_dir)

print('Getting existing projects from namespace %s...'%args.source_namespace)
s = requests.Session()
page_id = 1
finished = False
project_list = []
while not finished:
    print('Getting page %s'%page_id)
    res = s.get(gitlab_url + '/projects?private_token=%s&page=%s'%(gitlab_token,page_id))
    assert res.status_code == 200, 'Error when retrieving the projects. The returned html is %s'%res.text
    project_list += json.loads(res.text)
    if len(json.loads(res.text)) < 1:
        finished = True
    else:
        page_id += 1

filtered_projects = list(filter(lambda x: x['path_with_namespace'].split('/')[0]==args.source_namespace, project_list))

print('\n\nFinished preparations. We are about to migrate the following projects:')

print('\n'.join([p['path_with_namespace'] for p in filtered_projects]))

if 'yes' != input('Do you want to continue? (please answer yes or no) '):
    print('\nYou decided to cancel...')


for i in range(len(filtered_projects)):
    src_name = filtered_projects[i]['name']
    src_url = filtered_projects[i]['ssh_url_to_repo']
    src_description = filtered_projects[i]['description']
    dst_name = src_name.replace(' ','-')

    print('\n\nMigrating project %s to project %s now.'%(src_url,dst_name))
    if 'yes' != input('Do you want to continue? (please answer yes or no) '):
        print('\nYou decided to cancel...')

    # Create repo 
    if args.add_to_private:
        create_repo = s.post(gogs_url+'/user/repos', data=dict(token=gogs_token, name=dst_name, private=True))
    elif args.add_to_organization:
        create_repo = s.post(gogs_url+'/org/%s/repos'%args.add_to_organization, 
                            data=dict(token=gogs_token, name=dst_name, private=True, description=src_description))
    if create_repo.status_code != 201:
        print('Could not create repo %s because of %s'%(src_name,json.loads(create_repo.text)['message']))
        if 'yes' != input('Do you want to skip this repo and continue with the next? (please answer yes or no) '):
            print('\nYou decided to cancel...')
            exit(1)
        continue
    
    dst_info = json.loads(create_repo.text)

    dst_url = dst_info['ssh_url']
    # Git pull and push
    subprocess.check_call(['git','clone','--bare',src_url])
    os.chdir(src_url.split('/')[-1])
    subprocess.check_call(['git','push','--mirror',dst_url])
    os.chdir('..')
    subprocess.check_call(['rm','-rf',src_url.split('/')[-1]]) 

    print('\n\nFinished migration. New project URL is %s'%dst_info['html_url'])
    print('Please open the URL and check if everything is fine.')
    input('Hit any key to continue!')
    
print('\n\nEverything finished!\n')
