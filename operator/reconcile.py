import schedule
import time
import reconcile_docker
import reconcile_git

SCHEDULE_INTERVAL_MINUTES = 5


def reconcile():
    print("Checking for differences...")

    print("Running Git repository validation...")
    reconcile_git.reconcile()
    print("Running Docker configuration validation...")
    reconcile_docker.reconcile()


if __name__ == '__main__':
    # Schedule the reconcile function to run every 5 minutes
    print(f"Starting reconcile scheduler with a {SCHEDULE_INTERVAL_MINUTES} minutes interval...")
    schedule.every(SCHEDULE_INTERVAL_MINUTES).minutes.do(reconcile)

    # Infinite loop to continuously run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)  # You can adjust the sleep time if needed
