import urllib.request

resp = urllib.request.urlopen('http://localhost:8000/')
html = resp.read().decode()

# Find everything between </style> and </head>
style_end = html.find('</style>')
head_end = html.find('</head>')
if style_end > 0 and head_end > 0:
    print("Content between </style> and </head>:")
    print(repr(html[style_end+8:head_end]))
else:
    print("Could not find style/head end tags")
    print("First 500 chars:", html[:500])
