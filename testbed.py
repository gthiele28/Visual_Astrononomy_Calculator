import re
#testDict = {"key": "val"}
#print(testDict["piss"])
str = "23.5 mag/arcsec<sup>2</sup>"
print(re.sub(r'[^0-9]', '', str))