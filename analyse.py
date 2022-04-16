#!/usr/bin/env python
import sys
import arrow
import csv
import country_converter as coco
import json
from haversine import haversine_vector, Unit

MIN_POP=500000 # minimum city population
RADIUS=25 # city radius

pct_users = {}
with open("API_IT.NET.USER.ZS_DS2_en_csv_v2_3930944.csv") as inf:
    reader = csv.reader( inf )
    for row in reader:
        if len( row ) > 1:
            cc3 = row[1]
            iso2_codes = coco.convert(names=[cc3], to='ISO2', not_found=None)
            if iso2_codes and len( iso2_codes ) == 2:
                val = None
                for i in range( len( row ) - 1, -1, -1): # walk backwards
                    val = row[i]
                    try:
                        val = float( val )
                        break
                    except:
                        pass
                if val:
                    pct_users[ iso2_codes ] = val

## some vals not found this way have to be estimated
pct_users['TW'] = (pct_users['CN'] + pct_users['KR'] + pct_users['JP']) / 3
pct_users['KP'] = 0 # https://en.wikipedia.org/wiki/Internet_in_North_Korea

up = [] # up probes

with open("probes.json",'rt') as inf:
    j = json.load( inf )
    for p in j['objects']:
        if not isinstance(p['latitude'], float) or not isinstance( p['longitude'], float):
            print( "EEP", p, file=sys.stderr )
            continue
        if p['status'] == 1: # connected
            up.append( {
                'prb_id': p['id'],
                'lat': p['latitude'],
                'lon': p['longitude']
            } )

'''
{'id': 1, 'address_v4': '45.138.229.91', 'address_v6': '2a10:3781:e22:1:220:4aff:fec8:23d7', 'asn_v4': 206238, 'asn_v6': 206238, 'prefix_v4': '45.138.228.0/22', 'prefix_v6': '2a10:3780::/29', 'is_anchor': False, 'is_public': True, 'status': 1, 'status_since': 1649331265, 'first_connected': 1288367583, 'total_uptime': 349801536, 'tags': ['system-ipv6-stable-1d', 'system-ipv6-stable-90d', 'system-ipv6-stable-30d', 'system-ipv4-stable-1d', 'system-resolves-aaaa-correctly', 'system-resolves-a-correctly', 'system-ipv6-works', 'system-ipv4-works', 'dsl', 'home', 'nat', 'native-ipv6', 'ipv6', 'system-v1', 'system-ipv6-capable', 'system-ipv4-rfc1918', 'xs4all', 'system-ipv4-capable', 'system-ipv4-stable-90d', 'system-ipv4-stable-30d'], 'country_code': 'NL', 'latitude': 52.3475, 'longitude': 4.9275, 'day': '20220414', 'probe': 'https://atlas.ripe.net/api/v2/probes/1/', 'status_name': 'Connected'}
print( p['objects'][0] )
 
['915883', 'Kafue', 'Kafue', 'Kafe,Kafue,Кафе', '-15.76911', '28.18136', 'P', 'PPL', 'ZM', '', '09', '', '', '', '47554', '', '996', 'Africa/Lusaka', '2012-01-17']
1 = name
4 = lat?
5 = lon?
8 = country
14 = pop


'''
cities = []

with open("cities15000.txt",'rt') as inf:    
    for line in inf:
        line = line.rstrip('\n')
        fields = line.split("\t")
        name = fields[1]
        lat = float( fields[4] )
        lon = float( fields[5] )
        cc = fields[8]
        pop = int( fields[14] )
        if pop > MIN_POP:
            cities.append({
                'name': name,
                'lat': lat,
                'lon': lon,
                'cc': cc,
                'pop': pop
            })

cities.sort( key=lambda x: x['pop'], reverse=True )

prb_coord = list( map(lambda x: (x['lat'],x['lon']) , up ) )
city_coord = list( map(lambda x: (x['lat'],x['lon']) ,cities ) )

#print( prb_coord )
#print( city_coord )

distances = haversine_vector(prb_coord, city_coord, Unit.KILOMETERS, comb=True)

j = {
  'radius': RADIUS,
  'min_pop': MIN_POP,
  'date':  arrow.now().format('YYYY-MM-DD'),
  'cities': []
}

for c_idx, city in enumerate( cities ):
    city_distances = distances[ c_idx ]
    close = filter( lambda x: x < RADIUS , city_distances )
    close_cnt = len( list( close ) ) 
    int_pop = int( city['pop'] * 0.01 * pct_users[ city['cc'] ] )
    print( f"{city['name']}, {city['cc']}, {city['pop']}, {int_pop}, {close_cnt}" )
    j['cities'].append({
        'city': city['name'],
        'lat': city['lat'],
        'lon': city['lon'],
        'country': city['cc'],
        'city_population': city['pop'],
        'city_internet_population': int_pop,
        f'atlas_probe_{RADIUS}km_count': close_cnt
    })

with open(f"cities.atlas.r{RADIUS}.m{MIN_POP}.json", 'wt') as outf:
    json.dump( j, outf, indent=2 )
