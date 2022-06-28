import argparse

from github import Github, Repository, GithubException
import csv


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', type=str, required=True, help='token github account')
    parser.add_argument('-l', '--list', type=str, required=True, help='repos names file')
    return parser.parse_args()


def login(token):
    client = Github(login_or_token=token)
    try:
        client.get_user().login
    except GithubException as err:
        print(f'Github: Connect: error {err.data}')
        raise Exception('Github: Connect: user could not be authenticated please try again.')
    return client


def log_commit_to_csv(info, csv_name):
    fieldnames = ['repository name', 'author name', 'email', 'date and time', 'changed files']
    with open(csv_name, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(info)


def log_commit_to_stdout(info):
    print(info)


def log_repository_commits(repository: Repository, csv_name):
    for commit in repository.get_commits():
        info = {'repository name': repository.name, 'author name': commit.commit.author.name,
                'email': commit.commit.author.email, 'date and time': commit.commit.author.date.ctime(),
                'changed files': ', '.join([file.filename for file in commit.files])}

        log_commit_to_csv(info, csv_name)
        log_commit_to_stdout(info)


def log_issue_to_csv(info, csv_name):
    fieldnames = ['repository name', 'number', 'title', 'state', 'task', 'created at', 'author name', 'email']
    with open(csv_name, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(info)


def log_issue_to_stdout(info):
    print(info)


def log_repository_issues(repository: Repository, csv_name):
    for issue in repository.get_issues(state='all'):
        author = issue.user
        info = {'repository name': repository.name, 'number': issue.number, 'title': issue.title,
                'state': issue.state, 'task': issue.body, 'created at': issue.created_at.ctime(),
                'author name': '-' if author is None else author.name,
                'email': '-' if author is None else author.url}
        log_issue_to_csv(info, csv_name)
        log_issue_to_stdout(info)


def log_repositories(client: Github, repositories, csv_name):
    # with open(csv_name, 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow(
    #         (
    #             'Название репозитория',
    #             'Имя',
    #             'Почта',
    #             'Дата и Время',
    #             'Список затронутых файлов'
    #         )
    #     )
    with open(csv_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'Название репозитория',
                'Номер issue',
                'Название issue',
                'Состояние',
                'Текст issue',
                'Дата и Время создания',
                'Имя автора',
                'Почта автора'
            )
        )
    with open(repositories, 'r') as file:
        list_repos = file.read().split('\n')
    for repo_name in list_repos:
        try:
            repo = client.get_repo(repo_name)
        except GithubException as err:
            print(f'Github: Connect: {err.data}')
            raise Exception(f'Github: Connect: failed to load repository {repo_name}')

        # log_repository_commits(repo, csv_name)
        log_repository_issues(repo, csv_name)


def main():
    # args = parse_args()
    # token = args.token
    # repositories = args.list
    # csv_name = args.filename
    token = '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'
    repositories = 'list_repos.txt'
    csv_name = 'repos_stats.csv'
    try:
        client = login(token=token)
        log_repositories(client=client, repositories=repositories, csv_name=csv_name)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
