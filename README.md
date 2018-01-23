tbldifconv
==========

Convert Thunderbird address ldif to your ldap ldif.

Required
--------

* python3.6.x

How to use
----------

	tbldifconv.py  -b YOUR_LDAP_BASE_PATH  FILE_OF_THUNDERBIRD_LDIF

example operation
-----------------

	$ python tbldifconv.py -b ou=Address,dc=example,dc=com thunderbird.ldif > address.ldif
	$ ldapadd -D cn=Manager,dc=example,dc=com -W -f address.ldif
