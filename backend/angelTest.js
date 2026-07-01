require("dotenv").config();

const { SmartAPI } = require("smartapi-javascript");

const smart = new SmartAPI({
    api_key: process.env.ANGEL_API_KEY
});

smart.requestHeaders = {
    "X-ClientLocalIP": "127.0.0.1",
    "X-ClientPublicIP": "127.0.0.1",
    "X-MACAddress": "02:4b:66:09:cc:89",
    "Accept": "application/json",
    "X-PrivateKey": process.env.ANGEL_API_KEY,
    "X-UserType": "USER",
    "X-SourceID": "WEB"
};

(async () => {

    try {

        const clientId = "J318997";
        const password = "2003";
        const totp = "403990";

        console.log("Logging in...");

        const session = await smart.generateSession(
            clientId,
            password,
            totp
        );

        console.log("SESSION RESPONSE");
        console.log(JSON.stringify(session, null, 2));

    } catch (e) {

        console.log(e);

    }

})();
