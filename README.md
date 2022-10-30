# DigestBreaker

Made to brute force a Meraki MX100 at school for fun. ~~I was going to make my own MD5 Digest auth implementation and actually learn something about headers and requests and http auth etc. but that was apparently already done for me so idk what else to do here.~~ I generalized most of it but I don't have many test cases  to attempt on, so it might not work in some senarios. For example, I haven't implemented `auth-int`, but I do have opaques and the other qop's working.

My implementation (`run.py`) makes one request per auth attempt, as well as making it's own hashs and generally doing less safety checks. it's over twice the speed because it only does one request per auth attempt instead of two due to reusing the nonce, among other improvements and generally less checks.

~~TODO: check for qop and opaque, use if applicable (in effect combine `run.py`, `noqop.py`, and `opaque.py`(forgot to commit that one))~~\
~~TODO: do hashing all in one function, with a variable amount of params and joining of vars with ':'~~

How to use:\
idk change some vars
