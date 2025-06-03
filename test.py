import subprocess, threading, time, os, signal, shlex

def run_ffmpeg(device, outfile="out.m4a", bitrate="128k"):
    cmd = [
        "ffmpeg", "-hide_banner",
        "-f", "dshow", "-i", f"audio={device}",
        "-c:a", "aac", "-b:a", bitrate,
        "-y",
        "-progress", "-",      # <-- статистика в stdout
        "-nostats",            # убираем «size=…» в stderr
        outfile
    ]
    # text=True => строки, bufsize=1 => построчная буферизация
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True, bufsize=1)

    def reader():
        while proc.poll() is None:
            line = proc.stdout.readline().strip()
            if line:
                # progress-формат: key=value
                if "=" in line:
                    print(line)
                    print('---')
                    k, v = line.split("=", 1)
                    if k in ("out_time_ms", "out_time", "speed", "total_size"):
                        pass
                        # print(f"{k}: {v}")
        proc.stdout.close()

    th = threading.Thread(target=reader, daemon=True); th.start()
    return proc

if __name__ == "__main__":
    p = run_ffmpeg("Стерео микшер (Realtek(R) Audio)", "rec.m4a")
    time.sleep(15)              # пишем 15 с
    if os.name == "nt":
        p.send_signal(signal.CTRL_BREAK_EVENT)
    else:
        p.terminate()
    p.wait()
