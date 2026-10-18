url='https://www.narcconline.org/narcc/Repeater_List_Menu.cfm?CZONE=South%20Bay&SBAND=144&SType=All&Status=All'

from bs4 import BeautifulSoup
import requests
import csv


data = [
	{
		'zone': 'South%20Bay',
		'band': '1240',
		'bank': 'Bank00',
	},
	{
		'zone': 'East%20Bay',
		'band': '1240',
		'bank': None,
	},
	{
		'zone': 'West%20Bay',
		'band': '1240',
		'bank': None,
	},
	{
		'zone': 'North%20Bay',
		'band': '1240',
		'bank': None,
	},
	{
		'zone': 'Central%20Coast',
		'band': '1240',
		'bank': None,
	},
	{
		'zone': 'South%20Bay',
		'band': '144',
		'bank': 'Bank01',
	},
	{
		'zone': 'East%20Bay',
		'band': '144',
		'bank': None,
	},
	{
		'zone': 'West%20Bay',
		'band': '144',
		'bank': None,
	},
	{
		'zone': 'North%20Bay',
		'band': '144',
		'bank': None,
	},
	{
		'zone': 'South%20Bay',
		'band': '440',
		'bank': 'Bank03',
	},
	{
		'zone': 'East%20Bay',
		'band': '440',
		'bank': None,
	},
	{
		'zone': 'West%20Bay',
		'band': '440',
		'bank': None,
	},
	{
		'zone': 'North%20Bay',
		'band': '440',
		'bank': None,
	},
	{
		'zone': 'North%20Bay',
		'band': '440',
		'bank': None,
	},
	{
		'zone': 'North%20Bay',
		'band': '440',
		'bank': None,
	},
	{
		'zone': 'Central%20Coast',
		'band': '144',
		'bank': 'Bank08',
	},
	{
		'zone': 'Central%20Coast',
		'band': '440',
		'bank': None,
	},
]

f=open('/Users/n6il/tmp/djg7-old.CSV')
c=csv.reader(f)
table = []
for l in c:
	table.append(l)



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

	# Alinco
	# ['', 'Freqency', 'mode', 'step', 'Carrier', 'Tone/DCS', 'Tx-tone', 'Rx-tone', 'DCS', 'Shift', 'Shift-Freq', 'Skip', 'Name', '0']
	# ['Bank02-000', '145.23000', 'FM', '5KHz', 'JR', 'TSQ', '100.0Hz', '100.0Hz', '023', '-', '0.600MHz', '', 'N6NFI', '201']
	#print(['Banke2-000', '145.23000', 'FM', '5KHz', 'JR', 'TSQ', '100.0Hz', '100.0Hz', '023', '-', '0.600MHz', '', 'N6NFI', '201'])
	if d['bank'] is not None:
		tidx=0
	nidx=0
	print('narcc', len(narcc))
	while tidx<len(table) and nidx<len(narcc):
		#print('tidx: ',tidx, 'nidx', nidx, 'table: ', len(table), 'bank', d['bank'])
		l = table[tidx]
		if d['bank'] is not None and not l[0].startswith(d['bank']):
			tidx += 1
			continue
		d['bank'] = None
		#print('tidx: ',tidx, 'nidx', nidx, 'table: ', len(table))
		output, inp, ctcss, call, location, sponsor, status, notes, typ=narcc[nidx]
		if 'Repeater' not in typ:
			print('skip: ',narcc[nidx], typ)
			nidx += 1
			continue
		mem = l[0]
		frequency = float(output)
		mode = 'FM'
		step='5KHz'
		carrier  = 'JR'
		tone = 'Tone' if ctcss else 'None'
		tonef = ctcss+'Hz' if ctcss else "100.0Hz"
		dcs = '023'

		f2 = float(inp)
		shift = '+' if f2>frequency else '-'
		shiftf = "%0.3fMHz" % round(abs(f2 - frequency), 3)
		skip = ''
		name = "%-15s" % (call+" "+sponsor) if call != sponsor else call
		num = l[-1]

		row = (
			mem,
			"%0.5f" % frequency,
			mode,
			step,
			carrier,
			tone,
			tonef,
			tonef,
			dcs,
			shift,
			shiftf,
			skip,
			name,
			num
			)

		print(table[tidx])
		print(row)
		table[tidx] = row
		tidx += 1
		nidx+=1
		if nidx==len(narcc):
			break

with open('/Users/n6il/tmp/djg7-test.CSV', 'w', newline='') as f:
	writer = csv.writer(f, quotechar='"', quoting=csv.QUOTE_ALL)
	writer.writerows(table)

