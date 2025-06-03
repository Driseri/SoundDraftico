import subprocess
import re
import threading
import os
import signal
import time

def get_audio_lines():
    """Get Audio Sources"""
    result = subprocess.run(
        ['ffmpeg', '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8" 
    )
    output = result.stderr  # ffmpeg пишет устройства в stderr
    audio_devices = []
    for line in output.split('\n'):
        # Проверяем, что строка заканчивается на (audio)
        if line.strip().endswith('(audio)'):
            match = re.search(r'"([^"]+)"', line)
            if match:
                audio_devices.append(match.group(1))
    return audio_devices

class FFmpegProgressWatcher:
    def __init__(self, device_name, output_file="audio.mp3", bitrate="128k"):
        self.device_name = device_name
        self.output_file = output_file
        self.bitrate = bitrate
        self.process = None
        self.is_recording = False
        self._progress_thread = None
        self.last_progress = {}
        self._lock = threading.Lock()

    def start(self):
        if self.is_recording:
            return
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-f", "dshow",
            "-i", f"audio={self.device_name}",
            "-c:a", "libmp3lame",
            "-b:a", self.bitrate,
            "-y",
            "-progress", "-",    # Прогресс в stdout
            "-nostats",          # Не дублировать старый прогресс в stderr
            self.output_file
        ]
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True, bufsize=1)
        self.is_recording = True
        self._progress_thread = threading.Thread(target=self._watch_progress, daemon=True)
        self._progress_thread.start()

    def _watch_progress(self):
        while self.is_recording and self.process.poll() is None:
            line = self.process.stdout.readline()
            if not line:
                break
            line = line.strip()
            if "=" in line:
                key, value = line.split("=", 1)
                with self._lock:
                    self.last_progress[key] = value

    def stop(self):
        if not self.is_recording:
            return {
                "success": False,
                "reason": "Not recording.",
                "output_file": self.output_file
            }

        try:
            # Отправляем 'q' для корректной остановки ffmpeg
            if self.process.stdin:
                self.process.stdin.write('q\n')
                self.process.stdin.flush()
        except Exception as e:
            print(f"Ошибка при отправке 'q': {e}")

        self.is_recording = False

        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("FFmpeg не завершился за 5 секунд, принудительно завершаем...")
            self.process.kill()
            self.process.wait()

        with self._lock:
            out_time = self.last_progress.get("out_time", "00:00:00.00") or "00:00:00.00"
            size = self.last_progress.get("total_size", "0") or "0"
            speed = self.last_progress.get("speed", "0") or "0"

        success = os.path.exists(self.output_file) and os.path.getsize(self.output_file) > 0
        print(os.path.exists(self.output_file), os.path.getsize(self.output_file))
        return {
            "success": success,
            "output_file": self.output_file,
            "duration": out_time,
            "size_bytes": int(size) if str(size).isdigit() else 0,
            "speed": speed
        }

    def get_last_progress(self):
        with self._lock:
            # Можно вернуть всё, либо собрать короткую сводку
            out_time = self.last_progress.get("out_time", "00:00:00.00") or "00:00:00.00"
            size = self.last_progress.get("total_size", "0") or "0"
            speed = self.last_progress.get("speed", "0") or "0"
            return [out_time, size, speed]

if __name__ == "__main__":
    device = "Стерео микшер (Realtek(R) Audio)"  # Замени на свой девайс!
    watcher = FFmpegProgressWatcher(device, "test.mp3")
    watcher.start()
    print("Запись... Прогресс ffmpeg:")
    try:
        for _ in range(10):
            time.sleep(1)
            print(">>", watcher.get_last_progress())
        result = watcher.stop()
        print("Итог:", result)
        if result['success']:
            print(f"Файл {result['output_file']} успешно записан! Длительность: {result['duration']}, размер: {result['size_bytes']} байт.")
        else:
            print("Что-то пошло не так :(")
    except KeyboardInterrupt:
        watcher.stop()