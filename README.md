# DigestBreaker

Made to brute force a Meraki MX100 at school for fun. --I was going to make my own MD5 Digest auth implementation and actually learn something about headers and requests and http auth etc. but that was apparently already done for me so idk what else to do here.--

I made my own implementation but idk if it works correctly, so i'm keeping the old version as well. My implementation reuses the nonce and uses the nonce counter, as well as making it's own hashs. it's over twice the speed because it only does one request per auth, among other improvements.