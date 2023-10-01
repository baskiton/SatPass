import argparse
import datetime as dt
import dateutil.tz
import json
import pathlib
import sys

import ephem


def load_tle(tle_f):
    objects = {}

    with tle_f.open() as f:
        for line in f:
            names = set()
            while 0 < len(line) <= 69:
                names.add(line.strip())
                line = f.readline()

            names.add(int(line[2:7]))

            l1 = line.rstrip()
            l2 = f.readline().rstrip()
            for name in names:
                try:
                    objects[name] = ephem.readtle(str(name), l1, l2), (str(name), l1, l2)
                except ValueError as e:
                    if str(e).startswith('incorrect TLE checksum'):
                        print(f'ERROR: {name}: {e}', file=sys.stderr)
                    else:
                        raise e

    return objects


def calculate_pass(cfg, ephems, sat_name, start_t, n):
    break_elev = cfg.get('break_elev', 0)
    td0 = int(cfg.get('timedelta', 1))
    observer = ephem.Observer()
    observer.lat = str(cfg['lat'])
    observer.lon = str(cfg['lon'])
    observer.elev = cfg.get('alt', 0)
    observer.temp = cfg.get('temp', 0)
    observer.compute_pressure()
    ltz = dateutil.tz.tzlocal()
    sat: ephem.EarthSatellite = ephems.get(sat_name)[0]

    while n > 0:
        observer.date = start_t
        rise_t, rise_az, culm_t, culm_alt, set_t, set_az = observer.next_pass(sat, False)
        print(set_t, type(set_t), ephem.to_timezone(set_t, dt.timezone.utc))
        if culm_alt / ephem.degree < cfg['min_elev']:
            start_t = ephem.to_timezone(set_t, dt.timezone.utc) + dt.timedelta(minutes=1)
            continue

        n -= 1
        start_t = ephem.to_timezone(rise_t, dt.timezone.utc)
        set_t = ephem.to_timezone(set_t, dt.timezone.utc)

        observer.date = start_t
        sat.compute(observer)
        elev = sat.alt / ephem.degree
        while elev < break_elev:
            start_t += dt.timedelta(seconds=td0)
            observer.date = start_t
            sat.compute(observer)
            elev = sat.alt / ephem.degree

        fp = pathlib.Path(cfg['out_dir']).expanduser().absolute() / f'{sat_name} {start_t.astimezone(ltz).isoformat()}.txt'
        with fp.open('w') as f:
            td = 0
            while elev > break_elev and start_t < set_t:
                f.write(f'{td}\t{sat.az / ephem.degree:.01f}\t{elev:.01f}\n')

                td += td0
                start_t += dt.timedelta(seconds=td0)
                observer.date = start_t
                sat.compute(observer)
                elev = sat.alt / ephem.degree


def main(args):
    cfg = json.loads(open(args.config).read())
    ephems = load_tle(pathlib.Path(cfg['tle_file']).expanduser().absolute())
    start_t = args.t.astimezone(dt.timezone.utc)

    for s in args.sats.split(','):
        calculate_pass(cfg, ephems, s, start_t, args.n)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()

    ap.add_argument('config', type=pathlib.Path,
                    help='Path to config.json')
    ap.add_argument('sats',
                    help='Satellite names list to find passes, comma separated')
    ap.add_argument('-t', default=dt.datetime.now().isoformat(), type=dt.datetime.fromisoformat,
                    help='Start datetime to find passes in ISO format (e.g.: 2012-02-12 11:22:33), current by default')
    ap.add_argument('-n', default=1, type=int,
                    help='Num of satellite passes, 1 by default')

    main(ap.parse_args())
