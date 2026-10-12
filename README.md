# Smart Backup Rotator & Monitor (DevOps/SecOps Tool)

A production-ready Python automation script designed for efficient, secure, and idempotent backup replication and storage rotation across Windows Servers and local environments.

## 🚀 Key Features

* **Idempotency Check:** Uses `pathlib` to verify if the latest backup already exists at destinations before starting data transfer, preventing duplicate network load.
* **SecOps Pre-flight Safety:** Automatically calculates backup file size and checks target disk space via `shutil` before copying. Aborts safely if space is insufficient.
* **Resource-Friendly Transfer:** Streams large files (`.7z`, `.zip`, `.bak`) in 1MB binary chunks to prevent RAM spikes on legacy/low-resource production servers.
* **Visual Progress Bar:** Integrated with `tqdm` to display live compression speed and real-time copy progress in the console.
* **Storage Rotation (7-Day Retention):** Automatically acts as a janitor, scanning target directories and removing old backups older than 7 days using Unix timestamp evaluation.
* **Enterprise State Logging:** Generates structured, append-only YAML audit logs (`---` document delimiters) capturing timestamps, processed files, execution statuses (`Success`/`Error`), and dynamic rotation details.

## 🛠️ Infrastructure Environment
* Built and thoroughly tested on **Windows Server / Windows 7** platforms.
* Fully compatible with network UNC paths (`\\server\share`) and mapped network drives.
