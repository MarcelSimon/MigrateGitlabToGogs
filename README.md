# Migration utility for moving from Gitlab to Gogs / Gitea

This tools provides an automated way to copy all repositories in a namespaces from Gitlab to Gogs / Gitea. 
All tags and branches are copied. 
Organizations in Gogs are supported as well. 

## Usage

Type `python migrate_gitlab_to_gogs.py --help` for usage information. 
It will print 
```
usage: migrate_gitlab_to_gogs.py [-h] --source_namespace SOURCE_NAMESPACE
                                 [--add_to_private]
                                 [--add_to_organization organization_name]
                                 --source_repo SOURCE_REPO --target_repo
                                 TARGET_REPO

optional arguments:
  -h, --help            show this help message and exit
  --source_namespace SOURCE_NAMESPACE
                        The namespace in gitlab as it appears in URLs. For
                        example, given the repository address
                        http://mygitlab.com/harry/my-awesome-repo.git, it
                        shows that this repository lies within my personal
                        namespace "harry". Hence I would pass harry as
                        parameter.
  --add_to_private      If you want to add the repositories under your own
                        name, ie. not in any organisation, use this flag.
  --add_to_organization organization_name
                        If you want to add all the repositories to an
                        exisiting organisation, please pass the name to this
                        parameter. Organizations correspond to groups in
                        Gitlab. The name can be taken from the URL, for
                        example, if your organization is http://mygogs-
                        repo.com/org/my-awesome-organisation/dashboard then
                        pass my-awesome-organisation here
  --source_repo SOURCE_REPO
                        URL to your gitlab repo in the format
                        http://mygitlab.com/
  --target_repo TARGET_REPO
                        URL to your gogs / gitea repo in the format
                        http://mygogs.com/
```

## Requirements
This tools was written for Python 3 using the requests, json, subprocess, and argparse modules. 
