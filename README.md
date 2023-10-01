# SatsPass
Calculate the passage of a satellite over given coordinates (Observer) and save the result into separate files

### Installation
* [Install Python](https://www.python.org/downloads/)
* Download this repo
* *Optionally: prepare virtual environment*
  * Linux
    ```shell
    python3 -m venv venv
    source venv/bin/activate
    ```
  * Windows
    * cmd.exe
      ```shell
      python -m venv venv
      .\venv\Scripts\activate.bat
      ```
    * PowerShell
      ```shell
      python -m venv venv
      .\venv\Scripts\Activate.ps1
      ```
* Install dependencies
  ```shell
  pip install -r requirements.txt
  ```

### Usage
`app.py [-h] [-t T] [-n N] config sats`

positional arguments:
* `config`      Path to config.json
* `sats`        Satellite names list to find passes, comma separated

options:
* `-h, --help`  show this help message and exit
* `-t T`        Start datetime to find passes in ISO format (e.g.: 2012-02-12 11:22:33), `current` by default
* `-n N`        Num of satellite passes, `1` by default

For example:
```shell
python app.py "/path/to/config.json" "SAT1,SAT2,SAT3"
```

#### Output file format
Name: `<sat_name> <local__start_datetime>.txt`  
Line: `<seconds> <sat_azimuth> <sat_elevation>`


### Configure

| Field      | Type    | Description                                                           |
|------------|---------|-----------------------------------------------------------------------|
| lat        | Number  | Observer Latitude in degrees                                          |
| lon        | Number  | Observer Longitude in degrees                                         |
| alt        | Number  | Observer Sea Level Altitude in meters, `0.0` by default               |
| temp       | Number  | Observer Air temperature in Celsius deg, `0.0` by default             |
| timedelta  | Integer | Time step in seconds, `1` by default                                  |
| min_elev   | Number  | Minimum satellite elevation on pass, in degrees                       |
| break_elev | Number  | Start/Stop recording satellit elevation, in degrees, `0.0` by default |
| tle_file   | String  | Path to file containing TLE data                                      |
| out_dir    | String  | Path to store output files                                            |
