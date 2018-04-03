import xml.etree.ElementTree as ET
import unicodecsv as csv
import feedparser
import requests
import sys

# List of national parties
landelijk = ['VVD', 'Partij van de Arbeid', 'Partij voor de Vrijheid', 'SP', 'CDA', 'D66', 'ChristenUnie', 'GROENLINKS', 'SGP', 'Partij voor de Dieren', '50PLUS', 'DENK', 'Forum voor Democratie', 'DENK', 'ChristenUnie/SGP']

# Load and parse ANP Elections RSS feed
index = 'https://verkiezingsdienst.anp.nl/rss/verkiezingen/gr2018/index.rss'
feed = feedparser.parse(index)

# Assign current and last elections 
huidige_verkiezingen = 'GR18'
vorige_verkiezingen = 'GR14'

# Initialing output
with open('elections_raw.csv', 'w') as csv_out:
	writer = csv.writer(csv_out, delimiter='\t')
	row = [	'Gemeente', 
			'Partij', 
			'Lokale partij?', 
			'Definitieve uitslag?', 
			'%s - Percentage' % huidige_verkiezingen, 
			'%s - Stemmen' % huidige_verkiezingen, 
			'%s - Zetels' % huidige_verkiezingen, 
			'%s - Percentage' % vorige_verkiezingen, 
			'%s - Stemmen' % vorige_verkiezingen, 
			'%s - Zetels' % vorige_verkiezingen,
			]
	writer.writerow(row)

def write(data):
	row = [data['Gemeente'], data['Partij'], data['Lokaal'], data['Definitieve uitslag']]
	row += [data[huidige_verkiezingen][d] for d in data[huidige_verkiezingen]]
	row += [data[vorige_verkiezingen][d] for d in data[vorige_verkiezingen]]

	with open('elections_raw.csv', 'a') as csv_out:
		writer = csv.writer(csv_out, delimiter='\t')
		writer.writerow(row)

# Load items from feed (we're looking for municipalities)
for item in feed['items']:
	# Check whether item is a municipality, by checking for biggest party in last/current elections
	if item.has_key('media_grootste'):
		print 'Found municipality <%s>...' % item['title']

		r = requests.get(item['id']) # Load associated XML
		root = ET.fromstring(r.text.encode('utf-8')) # parse XML

		# Check data type: only crawling municipalities
		if root.attrib['type'] != 'Gemeente':
			raise Exception('<%s> is not a municipality but should be!') % item['title']
			sys.exit()
	
		# Check whether result is final/partial result
		if root.find('Status').text == 'Eindstand':
			definite = True
		else:
			definite = False

		# Election results are grouped by a 'Groep' per political party
		for uitslag in root.findall('Groep'):

			# But some groups contain overall results, exclude those
			if uitslag.attrib['type'] == 'Partij':
				partij = uitslag.find('KorteNaam').text
				print '\tFound party: <%s>.' % partij
				
				# data structure
				data =	{ 	'Gemeente' : item['title'],
							'Partij' : partij,
							'Lokaal' : True if partij not in landelijk else False, 
							huidige_verkiezingen : {},	
							vorige_verkiezingen : {},
							'Definitieve uitslag' : definite
					}
				
				# crawling both latest and prior elections
				for verkiezing in uitslag.findall('Verkiezing'):
					for r in verkiezing:
						data[verkiezing.attrib['code']][r.tag] = r.text

				# writing
				write(data)

print 'Done!'
	