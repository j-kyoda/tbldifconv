tbldifconv
==========

Convert Thunderbird address ldif to your LDAP ldif, or the reverse.

Required
--------

* python3.6.x

How to use
----------

* Convert Thunderbird ldif to LDAP ldif.

	tbldifconv.py -b YOUR_LDAP_BASE_PATH -f FILE_OF_THUNDERBIRD_LDIF

* Convert LDAP ldif to Thunderbird ldif.

	tbldifconv.py -f FILE_OF_LDAP_LDIF

example operation
-----------------

	$ python tbldifconv.py -b ou=Address,dc=example,dc=com -f thunderbird.ldif > address.ldif
	$ ldapadd -x -D cn=Manager,dc=example,dc=com -W -f address.ldif


	$ ldapsearch -LLL -o ldif-wrap=no -x -D cn=Manager,dc=example,dc=com -W -b ou=Address,dc=example,dc=com >ldap_out.ldif
	$ cat ldap_out.ldif | python tbldifconv.py -f -
