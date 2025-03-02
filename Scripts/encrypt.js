async function encryptData(plainText, secretKey) {
    const encoder = new TextEncoder();
    const encodedText = encoder.encode(plainText);
    
    // Convert secret key to CryptoKey
    const key = await crypto.subtle.importKey(
        "raw",
        new TextEncoder().encode(secretKey),
        { name: "AES-GCM" },
        false,
        ["encrypt"]
    );

    const iv = crypto.getRandomValues(new Uint8Array(12)); // Initialization Vector

    const encrypted = await crypto.subtle.encrypt(
        { name: "AES-GCM", iv: iv },
        key,
        encodedText
    );

    return {
        ciphertext: btoa(String.fromCharCode(...new Uint8Array(encrypted))),
        iv: btoa(String.fromCharCode(...iv))
    };
}

// Example usage
encryptData("Hello, World!", "your-secret-key-32bytes")
    .then(console.log)
    .catch(console.error);
