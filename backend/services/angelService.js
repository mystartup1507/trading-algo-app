const SmartApi =
  require(
    "smartapi-javascript"
  ).SmartAPI;

const connectAngelBroker =
  async ({
    apiKey,
    clientId,
    password,
    totp
  }) => {

    try {

      const smartApi =
        new SmartApi({
          api_key: apiKey
        });

      const session =
        await smartApi.generateSession(
          clientId,
          password,
          totp
        );

      return {
        success: true,
        data: session
      };

    } catch (error) {

      return {
        success: false,
        message:
          error.message
      };

    }

};

const placeOrder =
  async ({
    apiKey,
    clientId,
    password,
    totp,
    orderData
  }) => {

    try {

      const smartApi =
        new SmartApi({
          api_key: apiKey
        });

      await smartApi.generateSession(
        clientId,
        password,
        totp
      );

      const order =
        await smartApi.placeOrder(
          orderData
        );

      return {
        success: true,
        data: order
      };

    } catch (error) {

      return {
        success: false,
        message:
          error.message
      };

    }

};

const getProfileData =
  async ({
    apiKey,
    clientId,
    password,
    totp
  }) => {

    try {

      const smartApi =
        new SmartApi({
          api_key: apiKey
        });

      await smartApi.generateSession(
        clientId,
        password,
        totp
      );

      const profile =
        await smartApi.getProfile(
          clientId
        );

      const rms =
        await smartApi.getRMS();

      return {
        success: true,
        profile,
        rms
      };

    } catch (error) {

      return {
        success: false,
        message:
          error.message
      };

    }

};

module.exports = {
  connectAngelBroker,
  placeOrder,
  getProfileData
};