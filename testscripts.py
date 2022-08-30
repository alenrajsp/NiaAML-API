import multiprocessing as mp
import time
import queue

running_flag = mp.Value("i", 1)

def worker(running_flag, q):
    count = 1
    while True:
        if running_flag.value:
            print ("working {0} ...".format(count))
            count += 1
            q.put(count)
            time.sleep(1)
            if count > 3:
                # Simulate hanging with sleep
                print ("hanging...")
                time.sleep(1000)

def watchdog(q):
    """
    This check the queue for updates and send a signal to it
    when the child process isn't sending anything for too long
    """
    while True:
        try:
            msg = q.get(timeout=10.0)
        except queue.Empty as e:
            print ("[WATCHDOG]: Maybe WORKER is slacking")
            q.put("KILL WORKER")

def main():
    """The main process"""
    q = mp.Queue()

    workr = mp.Process(target=worker, args=(running_flag, q))
    wdog = mp.Process(target=watchdog, args=(q,))

    # run the watchdog as daemon so it terminates with the main process
    wdog.daemon = True

    workr.start()
    print ("[MAIN]: starting process P1")
    wdog.start()

    # Poll the queue
    while True:
        msg = q.get()
        if msg == "KILL WORKER":
            print ("[MAIN]: Terminating slacking WORKER")
            workr.terminate()
            time.sleep(0.1)
            if not workr.is_alive():
                print ("[MAIN]: WORKER is a goner")
                workr.join(timeout=1.0)
                print ("[MAIN]: Joined WORKER successfully!")
                q.close()
                break # watchdog process daemon gets terminated

if __name__ == '__main__':
    main()