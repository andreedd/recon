import reconcile_docker
import reconcile_git


def reconcile():
    # reconcile_docker.reconcile()
    reconcile_git.reconcile()


if __name__ == '__main__':
    reconcile()
