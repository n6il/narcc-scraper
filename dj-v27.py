url='https://www.narcconline.org/narcc/Repeater_List_Menu.cfm?CZONE=South%20Bay&SBAND=144&SType=All&Status=All'

from bs4 import BeautifulSoup
import requests
import csv


data = [
	{
		'zone': 'South%20Bay',
		'band': '220',
		'channel': 10,
	},
	{
		'zone': 'East%20Bay',
		'band': '220',
		'channel': None,
	},
	{
		'zone': 'West%20Bay',
		'band': '220',
		'channel': None,
	},
	{
		'zone': 'North%20Bay',
		'band': '220',
		'channel': None,
	},
	{
		'zone': 'Central%20Coast',
		'band': '220',
		'channel': None,
	},
]

f=open('/Users/n6il/tmp/djv27-old.CSV')
c=csv.reader(f)
table = [None] * 204
start = 0
tidx = 0
headers = ['CHANNEL', 'VFO', 'CALL', 'RPT']
#print('# Alinco')
#print('# "MODEL", "BANK",  "CHANNEL","FREQUENCY","STEP","TONE","TXTONE", "RXTONE", "DCS","SHIFT","SHIFT FREQUENCY","Power","ATT","BS","Clock","BCLO","Name","Skip"')
#print('# "DJ-V27","MEMORY","1",      "224.6200", "5KHz","Tone","110.9Hz","110.9Hz","023","-Shift","1.6000","Lo","Off","On","Off","Off","KA2FND","Off"')
for l in c:
	#table.append(l)

	model, bank, channel, frequency, step, tone, txtone, rxtone, dcs, shift, shiftf, power, att, bs, clock, bclo, name, skip = l
	if channel in headers:
		channel = headers.index(channel)
	else:
		channel = int(channel)
		if channel == 0:
			start = tidx
	table[channel+start] = l
	print(tidx, channel+start, l)
	tidx += 1

channel = 10
tidx = start+channel
print(tidx, start)
for d in data:
	print(d)
	url='https://www.narcconline.org/narcc/Repeater_List_Menu.cfm?CZONE=%s&SBAND=%s&SType=All&Status=All' % \
		(d['zone'], d['band'])
	print(url)
	# Narcc
	# ['Output', 'Input', 'CTCSS', 'Call', 'Location', 'Sponsor', 'Status', 'Notes', 'Station Type'
	# ['1292.5500', '1272.5500', '88.5', 'WA6ITV', 'Palo Alto', 'WA6ITV', 'Uncoordinated', 'o', 'Repeater']
	r=requests.get(url)
	b=BeautifulSoup(r.text)
	rows=b.find_all('tr')
	header=[h.text.strip() for h in rows[2].find_all('td')]
	narcc=[]
	for row in rows[3:]:
		td=row.find_all('td')
		if len(td) < 9:
			continue
		output, inp, ctcss, call, location, sponsor, status, notes, typ=[h.text.strip() for h in td]
		narcc.append([output, inp, ctcss, call, location, sponsor, status, notes, typ])
		print(output, inp, ctcss, call, location, sponsor, status, notes, typ)

	print('# Alinco')
	print('# "MODEL", "BANK",  "CHANNEL","FREQUENCY","STEP","TONE","TXTONE", "RXTONE", "DCS","SHIFT","SHIFT FREQUENCY","Power","ATT","BS","Clock","BCLO","Name","Skip"')
	print('# "DJ-V27","MEMORY","1",      "224.6200", "5KHz","Tone","110.9Hz","110.9Hz","023","-Shift","1.6000","Lo","Off","On","Off","Off","KA2FND","Off"')
	if d['channel'] is not None:
		tidx=int(d['channel'])
		d['channel'] = None
	nidx=0
	print('narcc', len(narcc))
	while nidx<len(narcc):
		#print('tidx: ',tidx, 'nidx', nidx, 'table: ', len(table), 'channel', d['channel'])
		#print(table[tidx])
		#model, bank, channel, frequency, step, tone, txtone, rxtone, dcs, shift, shiftf, power, att, bs, clock, bclo, name, skip = table[tidx]
		d['channel'] = None
		#print('tidx: ',tidx, 'nidx', nidx, 'table: ', len(table))
		output, inp, ctcss, call, location, sponsor, status, notes, typ=narcc[nidx]
		if 'Repeater' not in typ:
			print('skip: ',narcc[nidx], typ)
			nidx += 1
			continue
		model = "DJ-V27"
		bank = "MEMORY"
		# channel = str(channel )
		frequency = float(output)
		mode = 'FM'
		step='5KHz'
		carrier  = 'JR'
		tone = 'Tone' if ctcss else 'None'
		txtone = rxtone = ctcss+'Hz' if ctcss else "100.0Hz"
		dcs = '023'

		f2 = float(inp)
		shift = '+Shift' if f2>frequency else '-Shift'
		shiftf = "%0.4f" % round(abs(f2 - frequency), 3)
		power = 'Lo'
		att = "Off"
		bs = "On"
		clock = "Off"
		bclo = "Off"
		name = "%-8s" % call if sponsor == call else sponsor
		skip = 'Off'

		if nidx == 0:
			_name = "*"+d['zone'].upper().replace('%20', ' ')
			row = ["DJ-V27","MEMORY",str(tidx),"223.5000","5KHz","None","100.0Hz","100.0Hz","023","None","1.6000","Hi","Off","On","On","Off","%-8s" % _name[:8],"Off"]
			table[tidx] = row
			tidx += 1
			channel+=1
		row = (
			model,
			bank,
			str(channel),
			"%0.4f" % frequency,
			step,
			tone,
			txtone,
			rxtone,
			dcs,
			shift,
			shiftf,
			power,
			att,
			bs,
			clock,
			bclo,
			name.upper(),
			skip
			)

		#print(table[tidx])
		print(tidx, row)
		table[tidx] = row
		tidx += 1
		nidx+=1
		channel+=1
		if nidx==len(narcc):
			break


table = [e for e in table if e is not None]
with open('/Users/n6il/tmp/djv27-test.CSV', 'w', newline='') as f:
	writer = csv.writer(f, quotechar='"', quoting=csv.QUOTE_ALL)
	writer.writerows(table)

