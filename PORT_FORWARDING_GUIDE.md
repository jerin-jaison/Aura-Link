# How to Forward Ports (Access Your Local Server)

To view your Client Player on another device (like a TV or phone), you need to expose your local server. Here are the 3 best ways to do it.

## Option 1: VS Code Built-in Port Forwarding (Easiest)
If you are using VS Code, you can do this directly in the editor.

1.  Open the **Ports** view (Press `Ctrl + ~` to open terminal, then click the **Ports** tab).
2.  Click **Forward a Port**.
3.  Enter **8000** and press Enter.
4.  Right-click the new `localhost:8000` entry and set **Port Visibility** to **Public**.
5.  Copy the "Forwarded Address" URL.
6.  Open that URL on your other device.

## Option 2: Using ngrok (Best for external sharing)
If VS Code forwarding is slow or blocked, use **ngrok**.

1.  Download ngrok from [ngrok.com](https://ngrok.com/download).
2.  Open a terminal and run:
    ```powershell
    ngrok http 8000
    ```
3.  It will give you a link like `https://a1b2-c3d4.ngrok-free.app`.
4.  Open that link on your TV/Phone.

## Option 3: Local Network (Zero config)
If your TV/Phone is on the **same WiFi** as your PC:

1.  Find your PC's IP address:
    - Open Terminal.
    - Run `ipconfig`.
    - Look for **IPv4 Address** (e.g., `192.168.1.3`).
2.  Start your Django server allowing all hosts:
    ```powershell
    python manage.py runserver 0.0.0.0:8000
    ```
3.  On your TV/Phone, go to:
    `http://192.168.1.3:8000/client/player/`
    *(Replace `192.168.1.3` with your actual IP)*.

> **Note:** Options 1 & 2 use HTTPS (secure), while Option 3 uses HTTP. Some browsers block autoplay on HTTP, so you might need to tap the screen once.
