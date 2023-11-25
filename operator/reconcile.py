import schedule
import time
import reconcile_docker
import reconcile_git


def reconcile():
    reconcile_docker.reconcile()
    reconcile_git.reconcile()


if __name__ == '__main__':
    # Schedule the reconcile function to run every 5 minutes
    schedule.every(5).minutes.do(reconcile)

    # Infinite loop to continuously run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)  # You can adjust the sleep time if needed
