# Build Kivy Application with Buildozer for Mobile

- [Build Kivy Application with Buildozer for Mobile](#build-kivy-application-with-buildozer-for-mobile)
  - [Installation](#installation)
    - [1. WSL (Windows Subsystem for Linux)](#1-wsl-windows-subsystem-for-linux)
    - [2. Ubuntu Distribution](#2-ubuntu-distribution)
    - [3. Install Required Dependencies for Buildozer](#3-install-required-dependencies-for-buildozer)
  - [Build Your App using Buildozer](#build-your-app-using-buildozer)
    - [Build Procedure](#build-procedure)
    - [Build using Script](#build-using-script)
  - [Troubleshooting](#troubleshooting)
    - [1. Check if proper python version is available inside WSL](#1-check-if-proper-python-version-is-available-inside-wsl)

This guide provides step-by-step instructions on how to build your Kivy application for mobile platforms using
Buildozer. Follow the steps below to package your app for Android or iOS.

> [!NOTE]
> The app is built and tested on a Windows machine. Adjustments may be needed for other operating systems.

## Installation

### 1. WSL (Windows Subsystem for Linux)

- Buildozer can not be run natively on Windows. You need to install Windows Subsystem for Linux (WSL) first.
- Follow the official Microsoft documentation to install WSL: [Install WSL](https://learn.microsoft.com/en-us/windows/wsl/install).
- Update wsl to WSL 2 if you haven't done so using the command:

  ```bash
  wsl --update
  ```

### 2. Ubuntu Distribution

After installing WSL, install the Ubuntu distribution from the Microsoft Store.

Ubuntu version used during development: `Ubuntu-22.04`

Update and upgrade the packages:

```bash
sudo apt update
```

### 3. Install Required Dependencies for Buildozer

Official Buildozer installation instructions: [buildozer-installation](https://buildozer.readthedocs.io/en/latest/installation/#install-on-ubuntu-24-04).

1. Install required dependencies:

   ```bash
   sudo apt update
   sudo apt install -y git zip unzip openjdk-17-jdk python3-pip \
   python3-virtualenv autoconf libtool pkg-config zlib1g-dev \
   libncurses5-dev libncursesw5-dev libtinfo6 cmake libffi-dev \
   libssl-dev automake autopoint gettext
   ```

2. Cython installation:

   ```bash
   pip install cython
   ```

## Build Your App using Buildozer

### Build Procedure

> [!NOTE]
> An automated `build.sh` script is provided in the repository to streamline the build process.
> You can run this script to automate the steps below.

1. A spec file is required to build the app. You can create one using the command:

   ```bash
   buildozer init
   ```

   Running the above command will create a `buildozer.spec` file in your current directory.

2. Open the `buildozer.spec` file and modify the following lines according to your app's requirements. Key fields
   to modify:

   - `title`: Your app's title
   - `package.name`: Your app's package name
   - `package.domain`: Your app's domain
   - `source.dir`: ensure it points to the directory containing your main.py file
   - `version`: Your app's version
   - `requirements`: List of dependencies your app needs (e.g., `kivy`, `python3`, etc.)
   - `icon.filename`: Path to your app's icon file
   - `osx.python_version`: Set to `3` for Python 3.x
   - `osx.kivy_version`: Set to the Kivy version you are using (e.g., `2.3.1`)

3. To build the app for Android, run the following command:

   ```bash
   buildozer -v android debug
   ```

### Build using Script

> [!NOTE]
> For a cleaner build process, the build script removes any existing `.buildozer` directories.

1. Copy the contents of the `src` folder to your WSL environment. Preferably, place it in your home directory
   (`/home/your-username/projects/daily-expense-tracker-mobile`).

2. Open your WSL terminal and navigate to the `daily-expense-tracker-mobile` directory.
3. Run the build script:

   ```bash
   bash build.sh
   ```

## Troubleshooting

### 1. Check if proper python version is available inside WSL

1. Ensure that Python 3 is installed and accessible in your WSL environment. You can check the version by running:

   ```bash
   which python3
   ```

   It should return a valid path, e.g., `/usr/bin/python3`.

2. Check if proper version of python is available for Buildozer by running:

   ```bash
   python3 --version
   ```

   It should return `3.10.x`.

3. Ensure Python PATH from mnt is not interfering with WSL Python PATH. This can cause unexpected issues. When faced
   issues, try Windows PATH leakage inside WSL by running:

   ```bash
   nano ~/.bashrc
   ```

   Then add the following line at the end of the file. The below command contains 'Python313' which is specific to my
   system. You may need to adjust it based on your Windows Python installation folder name.

   ```bash
   export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v 'Python313' | paste -sd ':' -)
   ```

   Save the file and exit. Then run:

   ```bash
   source ~/.bashrc
   ```

   Verify the PATH change by running:

   ```bash
   echo $PATH | grep Python
   ```
