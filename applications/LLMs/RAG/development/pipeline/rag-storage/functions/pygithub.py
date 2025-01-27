
from github import Github

def pygithub_get_repo_paths(
    token: str,
    owner: str, 
    name: str
) -> any:
    g = Github(token)
    repo = g.get_repo(f"{owner}/{name}")
    contents = repo.get_contents("")
    paths = []
    # This takes a long time
    # Consider data pararrelism
    while len(contents) > 0:
      file_content = contents.pop(0)
      if file_content.type == 'dir':
        contents.extend(repo.get_contents(file_content.path))
      else:
        paths.append(file_content.path)
    g.close()
    return paths

def pygithub_get_repo_contents(
    token: str,
    owner: str, 
    name: str, 
    paths: str
) -> any:
    g = Github(token)
    repo = g.get_repo(f"{owner}/{name}")
    contents = []
    for path in paths:
      try:
        file_content = repo.get_contents(path)
        content = file_content.decoded_content.decode('utf-8')
        contents.append(content)
      except Exception as e:
        print('Get content error with path ' + str(path))
        print(e)
        contents.append(None)
    g.close()
    return contents
