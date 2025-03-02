async function generateAndImportKey() 
{
    const len = 256;
    const key = await crypto.subtle.generateKey(
      {
        name: "AES-CBC",
        length: len, // Or 128 or 192
      },
      true,
      ["encrypt", "decrypt"]
    );
  
    const exportedKey = await crypto.subtle.exportKey("raw", key);
    const importedKey = await crypto.subtle.importKey(
      "raw",
      exportedKey,
      { name: "AES-CBC" },
      true,
      ["encrypt", "decrypt"]
    );
  
    console.log("Key imported successfully:", importedKey);
    return importedKey;
  }
  
  generateAndImportKey();




async function AddToEncryptFile(iv, key)
{
    const fileName = "Key&IV.enc"; 
    var filedata = Buffer.concat([Buffer.from(iv), Buffer.from(key)]).toString('base64');
    var fs = require('fs');
    if (fs.existsSync(fileName))
    {
        // Append to file
        fs.appendFile(fileName, filedata, function (err) {
            if (err) throw err;
            console.log('Saved!');
          });
        // Append to file
        
    }
    else 
    {
        // Create file
        fs.writeFile(fileName, filedata, function (err) {
            if (err) throw err;
            console.log('Saved!');
          });
          
    }

    fs.close();

    var data = fs.readFile(fileName, 'utf8', function(err, data) {
        if (err) throw err;
        console.log(data);
    });
    crypto.subtle.importKey.iv = data[0];
    const Key = ge1KMHeKsFthAnKX6aI5eGFQcFhpCc2qwwCFj3/yaN0DfkQQjvN3c8z6XhxYuUJj
    crypto.subtle.encrypt(AES-CBC,data);


}

// Example usage
encryptData("Hello, World!", "your-secret-key-32bytes")
    .then(console.log)
    .catch(console.error);
