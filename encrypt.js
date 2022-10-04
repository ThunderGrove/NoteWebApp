function getMsgEncoding(){
	const msgBox = document.getElementById("note").value;
	var msg = msgBox.value;
	var enc = new TextEncoder();
	return enc.encode(message);
}

async function encode(){
	var encoded = getMsgEncoding();
	//iv will be needed for decryption
	var iv = window.crypto.getRandomValues(new Uint8Array(16));
	//alert(iv);
	document.getElementById("iv").value = iv;
	var key = await window.crypto.subtle.generateKey({
		name: "AES-CBC",
		length: 256
		},
		true,
		["encrypt", "decrypt"]
	);

	const exported = await window.crypto.subtle.exportKey("raw", key);
	const exportedKeyBuffer = new Uint8Array(exported);
	document.getElementById("key").value = exportedKeyBuffer;
	var result = await window.crypto.subtle.encrypt({
		name: "AES-CBC",
		iv: iv
		},
		key,
		encoded
	);
	var decoder = new TextDecoder("utf-8");
	var cipherTextRaw = decoder.decode(result);
	var buffer = new Uint8Array(result);
	var cipherTextArr = `${buffer}...[${result.byteLength} bytes total]`;
	//document.getElementById("cryptTextArea").value="Krypteret besked: " + cipherTextRaw;
	//HER KRYPTERER VI NOTETEXT
	//document.getElementById("encodedTextArea").value="Krypteret besked: " + cipherTextArr;
	document.getElementById("note").value=cipherTextArr;
}

async function decode(){
	var msg=document.getElementById("note").value;
	var key=Array.from(document.getElementById("key").value);
	var iv=document.getElementById("iv").value;

	var result = await window.crypto.subtle.decrypt({
		name: "AES-CBC",
		iv: iv
		},
		key,
		msg
	);

	var decoder = new TextDecoder("utf-8");
	var cipherTextRaw = decoder.decode(result);
	var buffer = new Uint8Array(result);
	var cipherTextArr = `${buffer}...[${result.byteLength} bytes total]`;
	document.getElementById("note").value=cipherTextArr;
}

function getMsgEncoding(){
  var msg = document.getElementById("note").value;
  var enc = new TextEncoder();
  return enc.encode(msg);
}

function encryptMsg(key){
	var encoded = getMsgEncoding();
	// iv will be needed for decryption
	iv = window.crypto.getRandomValues(new Uint8Array(16));
	return window.crypto.subtle.encrypt({
		name: "AES-CBC",
		iv: iv
		},
		key,
		encoded
	);
}

function decryptMsg(key){
	var encoded = getMsgEncoding();
	// iv will be needed for decryption
	iv = window.crypto.getRandomValues(new Uint8Array(16));
	return window.crypto.subtle.decrypt({
		name: "AES-CBC",
		iv: iv
		},
		key,
		encoded
	);
}
