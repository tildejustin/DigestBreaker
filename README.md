# DigestBreaker

Made to brute force a Meraki MX100 at school for fun. ~~I was going to make my own MD5 Digest auth implementation and actually learn something about headers and requests and http auth etc. but that was apparently already done for me so idk what else to do here.~~

I made my own implementation but idk if it works correctly, so i'm keeping the old version as well. My implementation reuses the nonce and actually makes use of the nonce counter, as well as making it's own hashs. it's over twice the speed because it only does one request per auth attempt instead of two due to reusing the nonce, among other improvements and generally less checks.

TODO: check for stale nonce in header and request a new one at that point, and make sure to subtract from total at that point\
TODO: check for qop and opaque, use if applicable (in effect combine run.py, noqop.py, and opaque.py(forgot to commit that one))\
~~TODO: do hashing all in one function, with a variable amount of params and joining of vars with ':'~~