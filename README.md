# cpu-scheduler
[![CodeFactor](https://www.codefactor.io/repository/github/grantslape/cpu-scheduler/badge)](https://www.codefactor.io/repository/github/grantslape/cpu-scheduler)

A simple discrete discrete-time event simulator for a number of CPU schedulers on a single CPU system.

![Example Image](https://i.imgur.com/sfwh5uX.png)

## Dependencies
* Python 3
* Pandas
* Matplotlib
* Others, see `requirements.txt`

The dependencies take a while to install, (especially Pandas) so just be patient during first time setup.

## Usage

Run with default configuration:
```shell
$ source run.sh
Sim running, please be patient
Sim done, execution time: 168.723174
Plot is at data/1541391135/plots/plot.png
$ deactivate
$ open data/1541391135/plots/plot.png
```

Advanced usage:
```shell
$ python3 -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
$ python main.py <LENGTH> <MAX_RATE> <BASE_SEED>
Sim running, please be patient
Sim done, execution time: 168.723174
Plot is at data/1541391135/plots/plot.png
$ deactivate
$ open data/1541391135/plots/plot.png
```
Where:
* `LENGTH`: The number of processes to simulate
* `MAX_RATE`: From 1 to `MAX_RATE` processes per second arrival will be simulated, so if `MAX_RATE` equals 30, 30 different simulations will be run for each schedule type
* `BASE_SEED`: The base seed for the pseudo-random number generator.  Simulations of the same rate will have the same base seed for comparision purposes 