const crypto = require('crypto');
const fs = require('fs').promises;

async function generateAndImportKey() {
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

async function addToEncryptFile(iv, key) {
    const fileName = "Key&IV.enc";

    // Convert IV and key to buffers
    const exportedKey = await crypto.subtle.exportKey("raw", key);
    const fileData = Buffer.concat([Buffer.from(iv), Buffer.from(exportedKey)]).toString('base64');

    try {
        await fs.appendFile(fileName, fileData + '\n'); // Append new line for separation
        console.log('Key and IV saved to file.');
    } catch (err) {
        console.error("Error writing file:", err);
    }

    try {
        const data = await fs.readFile(fileName, 'utf8');
        console.log("File Contents:\n", data);
    } catch (err) {
        console.error("Error reading file:", err);
    }
}

async function encryptData(plainText, key) {
    const iv = crypto.getRandomValues(new Uint8Array(16)); // Generate a random IV

    const encoder = new TextEncoder();
    const data = encoder.encode(plainText);

    const encrypted = await crypto.subtle.encrypt(
        { name: "AES-CBC", iv: iv },
        key,
        data
    );

    console.log("Encrypted Data:", Buffer.from(encrypted).toString('base64'));

    // Save IV and key to a file
    await addToEncryptFile(iv, key);
}

// Run the functions
generateAndImportKey().then(key => encryptData("Hello, World!", key));
