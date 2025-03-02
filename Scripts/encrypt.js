async function generateAndImportKey() {
    const key = await crypto.subtle.generateKey(
      {
        name: "AES-CBC",
        length: 256, // Or 128 or 192
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

// Example usage
encryptData("Hello, World!", "your-secret-key-32bytes")
    .then(console.log)
    .catch(console.error);
