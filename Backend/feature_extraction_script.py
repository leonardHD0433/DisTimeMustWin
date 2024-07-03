import tldextract #Helps to splits url into its subdomain, domain, and suffix
import re
from urllib.parse import urlparse
import pandas as pd
import pickle
import hashlib
import pymssql
import requests 


#database connect
conn = pymssql.connect(
    server='example.database.windows.net',
    user='username',
    password='password',
    database='database_name',
    as_dict=True
)

#importing url from app logic here
#read from url.txt
with open("url.txt", "r") as f:
    url = f.read()

print(url)
  
#Check if URL already exists in database.
cursor = conn.cursor()
prediction_str = cursor.execute('SELECT type FROM URL WHERE url = %s', [url])
try :
    prediction_str = str(cursor.fetchone()['type'])
except TypeError:
    prediction_str = ""
conn.commit()
cursor.close()

#check if website certificate is valid
if (prediction_str==""):
    try :
        response = requests.get(url)
    except:
        print('Invalid SSL cert')
        prediction_str='unsecure'
        
        #store predicted label into database
        print('updating database')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO URL (url, type) VALUES (%s, %s)", (url, prediction_str))
        conn.commit()
        cursor.close()

    
#Perform ML analysis if both not in database and valid SSL certificate
if (prediction_str==""):
    urls_df = pd.DataFrame({"url":[url]})

    ##Normalize URLs
    urls_df['url'] = urls_df['url'].replace(to_replace = 'www.', value = '', regex = True)

    #Abnormal url
    #i) Help to identify URLs where domain part (netloc) appears in an unexpected part of the URL
    #ii) The function checks if the domain part of the URL appears elsewhere in the URL (useful heuristic for identifying potentially suspicious URLs)
    def is_abnormal_url(url):
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc
        if netloc:
            netloc = str(netloc)
            #To check if netloc (domain appears in an unexpected part of the URL)
            match = re.search(netloc, url)
            if match:
                return 1
                #if netloc found in URL, but not at the expected position, it is abnormal
        return 0

    urls_df['abnormal_url'] = urls_df['url'].apply(is_abnormal_url)

    # Function to extract whether the URL is secure (uses HTTPS)
    def extract_is_https(url):
        parsed_url = urlparse(url)
        return 1 if parsed_url.scheme == 'https' else 0

    # Apply the function to each URL and create a new column 'is_https'
    urls_df['is_https'] = urls_df['url'].apply(extract_is_https)    

    # Helper function to clean URLs
    def clean_url(url):
        return re.sub(r'^(http://|https://)', '', url)

    # Clean the URLs
    urls_df['cleaned_url'] = urls_df['url'].apply(clean_url)

    #Special characters count
    feature = ['@','?','-','=','.','#','%','+','$','!','*',',','//']
    for x in feature:
        urls_df[x] = urls_df['cleaned_url'].apply(lambda i: i.count(x))

    #Letters, Digits and Special Characters
    def count_letters(url): 
        no_of_letters = sum(char.isalpha() for char in url) #isalpha() checks if it is alphabets
        return no_of_letters

    def count_digits(url):
        no_of_digits = sum(char.isdigit() for char in url) 
        return no_of_digits

    urls_df['letters'] = urls_df['cleaned_url'].apply(count_letters)
    urls_df['digits'] = urls_df['cleaned_url'].apply(count_digits)

    #URL Length
    urls_df['url_length'] = urls_df['cleaned_url'].apply(lambda x: len(str(x)))

    #URL Domain
    def extract_primary_domain(url):
            try:
                ext = tldextract.extract(url)
                pri_domain = ext.domain+"."+ext.suffix #concatenate only the domain and suffix, thus, the primary domain
            except:  
                pri_domain = None #in case there is no primary domain to be found
            return pri_domain

    urls_df['primary_domain'] = urls_df['url'].apply(extract_primary_domain) #applied extraction of pri domain to each url and creating a new column for it

    #URL Region
    def get_url_region(primary_domain):
        ccTLD_to_region = {
        ".ac": "Ascension Island",
        ".ad": "Andorra",
        ".ae": "United Arab Emirates",
        ".af": "Afghanistan",
        ".ag": "Antigua and Barbuda",
        ".ai": "Anguilla",
        ".al": "Albania",
        ".am": "Armenia",
        ".an": "Netherlands Antilles",
        ".ao": "Angola",
        ".aq": "Antarctica",
        ".ar": "Argentina",
        ".as": "American Samoa",
        ".at": "Austria",
        ".au": "Australia",
        ".aw": "Aruba",
        ".ax": "Åland Islands",
        ".az": "Azerbaijan",
        ".ba": "Bosnia and Herzegovina",
        ".bb": "Barbados",
        ".bd": "Bangladesh",
        ".be": "Belgium",
        ".bf": "Burkina Faso",
        ".bg": "Bulgaria",
        ".bh": "Bahrain",
        ".bi": "Burundi",
        ".bj": "Benin",
        ".bm": "Bermuda",
        ".bn": "Brunei Darussalam",
        ".bo": "Bolivia",
        ".br": "Brazil",
        ".bs": "Bahamas",
        ".bt": "Bhutan",
        ".bv": "Bouvet Island",
        ".bw": "Botswana",
        ".by": "Belarus",
        ".bz": "Belize",
        ".ca": "Canada",
        ".cc": "Cocos Islands",
        ".cd": "Democratic Republic of the Congo",
        ".cf": "Central African Republic",
        ".cg": "Republic of the Congo",
        ".ch": "Switzerland",
        ".ci": "Côte d'Ivoire",
        ".ck": "Cook Islands",
        ".cl": "Chile",
        ".cm": "Cameroon",
        ".cn": "China",
        ".co": "Colombia",
        ".cr": "Costa Rica",
        ".cu": "Cuba",
        ".cv": "Cape Verde",
        ".cw": "Curaçao",
        ".cx": "Christmas Island",
        ".cy": "Cyprus",
        ".cz": "Czech Republic",
        ".de": "Germany",
        ".dj": "Djibouti",
        ".dk": "Denmark",
        ".dm": "Dominica",
        ".do": "Dominican Republic",
        ".dz": "Algeria",
        ".ec": "Ecuador",
        ".ee": "Estonia",
        ".eg": "Egypt",
        ".er": "Eritrea",
        ".es": "Spain",
        ".et": "Ethiopia",
        ".eu": "European Union",
        ".fi": "Finland",
        ".fj": "Fiji",
        ".fk": "Falkland Islands",
        ".fm": "Federated States of Micronesia",
        ".fo": "Faroe Islands",
        ".fr": "France",
        ".ga": "Gabon",
        ".gb": "United Kingdom",
        ".gd": "Grenada",
        ".ge": "Georgia",
        ".gf": "French Guiana",
        ".gg": "Guernsey",
        ".gh": "Ghana",
        ".gi": "Gibraltar",
        ".gl": "Greenland",
        ".gm": "Gambia",
        ".gn": "Guinea",
        ".gp": "Guadeloupe",
        ".gq": "Equatorial Guinea",
        ".gr": "Greece",
        ".gs": "South Georgia and the South Sandwich Islands",
        ".gt": "Guatemala",
        ".gu": "Guam",
        ".gw": "Guinea-Bissau",
        ".gy": "Guyana",
        ".hk": "Hong Kong",
        ".hm": "Heard Island and McDonald Islands",
        ".hn": "Honduras",
        ".hr": "Croatia",
        ".ht": "Haiti",
        ".hu": "Hungary",
        ".id": "Indonesia",
        ".ie": "Ireland",
        ".il": "Israel",
        ".im": "Isle of Man",
        ".in": "India",
        ".io": "British Indian Ocean Territory",
        ".iq": "Iraq",
        ".ir": "Iran",
        ".is": "Iceland",
        ".it": "Italy",
        ".je": "Jersey",
        ".jm": "Jamaica",
        ".jo": "Jordan",
        ".jp": "Japan",
        ".ke": "Kenya",
        ".kg": "Kyrgyzstan",
        ".kh": "Cambodia",
        ".ki": "Kiribati",
        ".km": "Comoros",
        ".kn": "Saint Kitts and Nevis",
        ".kp": "Democratic People's Republic of Korea (North Korea)",
        ".kr": "Republic of Korea (South Korea)",
        ".kw": "Kuwait",
        ".ky": "Cayman Islands",
        ".kz": "Kazakhstan",
        ".la": "Laos",
        ".lb": "Lebanon",
        ".lc": "Saint Lucia",
        ".li": "Liechtenstein",
        ".lk": "Sri Lanka",
        ".lr": "Liberia",
        ".ls": "Lesotho",
        ".lt": "Lithuania",
        ".lu": "Luxembourg",
        ".lv": "Latvia",
        ".ly": "Libya",
        ".ma": "Morocco",
        ".mc": "Monaco",
        ".md": "Moldova",
        ".me": "Montenegro",
        ".mf": "Saint Martin (French part)",
        ".mg": "Madagascar",
        ".mh": "Marshall Islands",
        ".mk": "North Macedonia",
        ".ml": "Mali",
        ".mm": "Myanmar",
        ".mn": "Mongolia",
        ".mo": "Macao",
        ".mp": "Northern Mariana Islands",
        ".mq": "Martinique",
        ".mr": "Mauritania",
        ".ms": "Montserrat",
        ".mt": "Malta",
        ".mu": "Mauritius",
        ".mv": "Maldives",
        ".mw": "Malawi",
        ".mx": "Mexico",
        ".my": "Malaysia",
        ".mz": "Mozambique",
        ".na": "Namibia",
        ".nc": "New Caledonia",
        ".ne": "Niger",
        ".nf": "Norfolk Island",
        ".ng": "Nigeria",
        ".ni": "Nicaragua",
        ".nl": "Netherlands",
        ".no": "Norway",
        ".np": "Nepal",
        ".nr": "Nauru",
        ".nu": "Niue",
        ".nz": "New Zealand",
        ".om": "Oman",
        ".pa": "Panama",
        ".pe": "Peru",
        ".pf": "French Polynesia",
        ".pg": "Papua New Guinea",
        ".ph": "Philippines",
        ".pk": "Pakistan",
        ".pl": "Poland",
        ".pm": "Saint Pierre and Miquelon",
        ".pn": "Pitcairn",
        ".pr": "Puerto Rico",
        ".ps": "Palestinian Territory",
        ".pt": "Portugal",
        ".pw": "Palau",
        ".py": "Paraguay",
        ".qa": "Qatar",
        ".re": "Réunion",
        ".ro": "Romania",
        ".rs": "Serbia",
        ".ru": "Russia",
        ".rw": "Rwanda",
        ".sa": "Saudi Arabia",
        ".sb": "Solomon Islands",
        ".sc": "Seychelles",
        ".sd": "Sudan",
        ".se": "Sweden",
        ".sg": "Singapore",
        ".sh": "Saint Helena",
        ".si": "Slovenia",
        ".sj": "Svalbard and Jan Mayen",
        ".sk": "Slovakia",
        ".sl": "Sierra Leone",
        ".sm": "San Marino",
        ".sn": "Senegal",
        ".so": "Somalia",
        ".sr": "Suriname",
        ".ss": "South Sudan",
        ".st": "São Tomé and Príncipe",
        ".sv": "El Salvador",
        ".sx": "Sint Maarten (Dutch part)",
        ".sy": "Syria",
        ".sz": "Eswatini",
        ".tc": "Turks and Caicos Islands",
        ".td": "Chad",
        ".tf": "French Southern Territories",
        ".tg": "Togo",
        ".th": "Thailand",
        ".tj": "Tajikistan",
        ".tk": "Tokelau",
        ".tl": "Timor-Leste",
        ".tm": "Turkmenistan",
        ".tn": "Tunisia",
        ".to": "Tonga",
        ".tr": "Turkey",
        ".tt": "Trinidad and Tobago",
        ".tv": "Tuvalu",
        ".tw": "Taiwan",
        ".tz": "Tanzania",
        ".ua": "Ukraine",
        ".ug": "Uganda",
        ".uk": "United Kingdom",
        ".us": "United States",
        ".uy": "Uruguay",
        ".uz": "Uzbekistan",
        ".va": "Vatican City",
        ".vc": "Saint Vincent and the Grenadines",
        ".ve": "Venezuela",
        ".vg": "British Virgin Islands",
        ".vi": "U.S. Virgin Islands",
        ".vn": "Vietnam",
        ".vu": "Vanuatu",
        ".wf": "Wallis and Futuna",
        ".ws": "Samoa",
        ".ye": "Yemen",
        ".yt": "Mayotte",
        ".za": "South Africa",
        ".zm": "Zambia",
        ".zw": "Zimbabwe"
        }
        
        for ccTLD in ccTLD_to_region:
            if primary_domain.endswith(ccTLD):
                return ccTLD_to_region[ccTLD]
        
        return "Global"

    urls_df['url_region'] = urls_df['primary_domain'].apply(lambda x: get_url_region(str(x)))

    #Root domain
    def extract_root_domain(url):
        extracted = tldextract.extract(url)
        root_domain = extracted.domain
        return root_domain

    urls_df['root_domain'] = urls_df['primary_domain'].apply(lambda x: extract_root_domain(str(x)))

    #Hash encode both url region and root domain
    def hash_encode(category):
        if category is None:
            return 0
        
        hash_object = hashlib.md5(category.encode())
        return int(hash_object.hexdigest(), 16) % (10 ** 8)

    urls_df['root_domain'] = urls_df['root_domain'].apply(hash_encode)
    urls_df['url_region'] = urls_df['url_region'].apply(hash_encode)

    #Shortened url (Checks to see whether URL containsa shortening service)
    def shortening_service(url):
        match = re.search(r'bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|'
                        r'yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|'
                        r'short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|'
                        r'doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|'
                        r'db\.tt|qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|'
                        r'q\.gs|is\.gd|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|'
                        r'x\.co|prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|'
                        r'tr\.im|link\.zip\.net', url)
        if match:
            return 1
        else:
            return 0
        
    urls_df['have_shortening_service'] = urls_df['url'].apply(shortening_service)

    #IP address
    def have_ip_address(url):
        ipv4_pattern = re.compile(      
            r'((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
            r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')

        ipv6_pattern = re.compile(r'\[?([A-Fa-f0-9]{1,4}:){7}([A-Fa-f0-9]{1,4}|:)\]?')

        # Check for IPv4 address
        if ipv4_pattern.search(url):
            return 1
        # Check for IPv6 address
        elif ipv6_pattern.search(url):
            return 1
        else:
            return 0

    urls_df['have_ip_address'] = urls_df['url'].apply(have_ip_address)

    x = urls_df.drop(['url', 'primary_domain', 'cleaned_url'], axis = 1)

    with open('maliciousURL_classifier_official.pkl', 'rb') as f:
        ml_classifier = pickle.load(f)

    #read predicted label into string
    prediction = ml_classifier.predict(x)
    prediction_str = str(prediction[0])  # Accessing the first element if it's an array

    #store predicted label into database
    print('updating database')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO URL (url, type) VALUES (%s, %s)", (url, prediction_str))
    conn.commit()
    cursor.close()

conn.close()

#write the predicted label to url_label.txt
with open("url_label.txt", "w") as f:
    f.write(prediction_str)
print(prediction_str)
