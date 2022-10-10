function getMsgEncoding(){
	var msgBox=document.getElementById("note").value;
	var msg=msgBox.value;
	var enc=new TextEncoder();
	return enc.encode(msg);
}

async function encode(){
	var encoded = getMsgEncoding();
	//iv will be needed for decryption
	var iv = window.crypto.getRandomValues(new Uint8Array(16));

	document.getElementById("iv").value=iv;

	var key = await window.crypto.subtle.generateKey({
		name: "AES-CBC",
		length: 256
		},
		true,
		["encrypt", "decrypt"]
	);

	var exported = await window.crypto.subtle.exportKey("raw", key);
	var exportedKeyBuffer = new Uint8Array(exported);
	document.getElementById("key").value = exportedKeyBuffer;

	var result = await window.crypto.subtle.encrypt({
		name:"AES-CBC",
		iv:iv
		},
		key,
		encoded
	);
	var decoder = new TextDecoder("utf-8");
	var cipherTextRaw = decoder.decode(result);
	var buffer = new Uint8Array(result);
	document.getElementById("note").value=buffer;
}

async function decode(){
	var msg=document.getElementById("note").value;
	msg=msg.base64Data;
	var key=Array.from(document.getElementById("key").value);
	var iv=document.getElementById("iv").value;
	iv=Array.from(iv);
	
	var uArray=new Uint8Array(
		[...msg].map((char)=>char.charCodeAt(0))
	);
	

	var algorithm = {
		name: "AES-GCM",
		iv:iv,
	};

	var imported = await window.crypto.subtle.importKey("raw", key,"AES-GCM",true,["encrypt", "decrypt"]);

	var decryptedData = await window.crypto.subtle.decrypt(
		algorithm,
		key,
		uArray
	);

	document.getElementById("note").value=new TextDecoder().decode(decryptedData);
}
