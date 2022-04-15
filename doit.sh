curl "http://download.geonames.org/export/dump/cities15000.zip" > cities15000.zip
unzip cities15000.zip
curl "https://ftp.ripe.net/ripe/atlas/probes/archive/meta-latest" > probes.json.bz2
bunzip2 probes.json.bz2
curl "https://api.worldbank.org/v2/en/indicator/IT.NET.USER.ZS?downloadformat=csv" > worldbank.inet-pop.csv.zip
unzip worldbank.inet-pop.csv.zip
./analyse.py > over1m.txt
