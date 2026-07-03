
const SmartApi =
  require(
    "smartapi-javascript"
  ).SmartAPI;

let smartApi = null;
let currentSession = null;

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
    api_key: apiKey,

    default_timeout: 5000
  });

smartApi.setSessionExpiryHook(
  () => {
    console.log(
      'Session Expired'
    );
  }
);

smartApi.requestHeaders = {
  'X-ClientLocalIP':
    '127.0.0.1',

  'X-ClientPublicIP':
    '127.0.0.1',

  'X-MACAddress':
    '02:4b:66:09:cc:89',

  'Accept':
    'application/json',

  'X-PrivateKey':
    apiKey,

  'X-UserType':
    'USER',

  'X-SourceID':
    'WEB'
};

const session =
  await smartApi.generateSession(
    clientId,
    password,
    totp
  );

console.log(
  JSON.stringify(session, null, 2)
);

return {
  success: true,
  data: session
};

} catch (error) {

  console.log("========== LTP API ERROR ==========");
  console.log(error);
  console.log("===================================");

  return {
    success: false,
    message: error.message,
    error
  };

}

};

const createSession =
  async ({
    apiKey,
    clientId,
    password,
    totp
  }) => {

if (
  smartApi &&
  currentSession &&
  currentSession.status === true
) {

  return smartApi;

}

    smartApi =
      new SmartApi({
        api_key: apiKey,
        default_timeout: 5000
      });

    smartApi.requestHeaders = {
      'X-ClientLocalIP': '127.0.0.1',
      'X-ClientPublicIP': '127.0.0.1',
      'X-MACAddress': '02:4b:66:09:cc:89',
      'Accept': 'application/json',
      'X-PrivateKey': apiKey,
      'X-UserType': 'USER',
      'X-SourceID': 'WEB'
    };

    currentSession =
      await smartApi.generateSession(
        clientId,
        password,
        totp
      );

    console.log("SESSION:");
    console.log(currentSession);

    if (
      !currentSession ||
      currentSession.status !== true
    ) {
      throw new Error("Angel Session Failed");
    }

    return smartApi;

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

if (!smartApi) {

  await createSession({
    apiKey,
    clientId,
    password,
    totp
  });

}

console.log("========== ORDER PAYLOAD ==========");
console.log(JSON.stringify(orderData, null, 2));

const order = await smartApi.placeOrder(orderData);

console.log("========== ORDER RESPONSE ==========");
console.log(JSON.stringify(order, null, 2));

if (
    order.status &&
    order.data &&
    order.data.orderid
) {

    const book =
        await smartApi.getOrderBook();

    console.log("========== ORDER BOOK ==========");

const failed = book.data.find(
    o => o.orderid === order.data.orderid
);

console.log(JSON.stringify(failed, null, 2));

}

console.log("========== ORDER RESPONSE ==========");
console.log(JSON.stringify(order, null, 2));

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

const getOrderBook = async ({
  apiKey,
  clientId,
  password,
  totp
}) => {

  try {

const smartApi = await createSession({
  apiKey,
  clientId,
  password,
  totp
});

    const orders = await smartApi.getOrderBook();

    return {
      success: true,
      data: orders
    };

  } catch (error) {

    return {
      success: false,
      message: error.message
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

      smartApi.requestHeaders = {

        'X-ClientLocalIP':
          '127.0.0.1',

        'X-ClientPublicIP':
          '127.0.0.1',

        'X-MACAddress':
          '02:4b:66:09:cc:89',

        'Accept':
          'application/json',

        'X-PrivateKey':
          apiKey,

        'X-UserType':
          'USER',

        'X-SourceID':
          'WEB'
      };

      const session =
        await smartApi.generateSession(
          clientId,
          password,
          totp
        );

      if (!session.status) {

        return {
          success: false,
          message:
            'Session Failed'
        };

      }

      return {
        success: true,

        profile: {
          data: {
            name:
              clientId
          }
        },

        rms: {
          data: {
            availablecash:
              session.data?.availablecash || 0
          }
        }
      };

    } catch (error) {

      return {
        success: false,
        message:
          error.message
      };

    }

};

const getPositions = async ({
  apiKey,
  clientId,
  password,
  totp
}) => {
  try {

const smartApi = await createSession({
    apiKey,
    clientId,
    password,
    totp
});

    const positions = await smartApi.getPosition();

    return {
      success: true,
      data: positions
    };

  } catch (error) {

    return {
      success: false,
      message: error.message
    };

  }
};

const getCandleData = async ({
  apiKey,
  clientId,
  password,
  totp,
  params
}) => {

  try {

     if (!smartApi) {

  await createSession({
    apiKey,
    clientId,
    password,
    totp
  });

}  

    const candles =
      await smartApi.getCandleData(
        params
      );

    return {
      success: true,
      data: candles
    };

  } catch (error) {

    return {
      success: false,
      message: error.message
    };

  }

};

const getLTPData = async ({
  apiKey,
  clientId,
  password,
  totp,
  params
}) => {

  try {

    if (!smartApi) {

      await createSession({
        apiKey,
        clientId,
        password,
        totp
      });

    }

    console.log("===== LTP REQUEST =====");
console.log(params);

const ltp = await smartApi.marketData({

    mode: "LTP",

    exchangeTokens: {

        [params.exchange]: [

            String(params.symboltoken)

        ]

    }

});

console.log("===== MARKET DATA =====");
console.log(JSON.stringify(ltp, null, 2));

return {
    success: true,
    data: ltp
};

}   catch (error) {

    console.log("===== LTP ERROR =====");
    console.log(error);

    return {
        success: false,
        message: error.message
    };

}


};

const getMarketData = async ({
  apiKey,
  clientId,
  password,
  totp,
  mode,
  exchange,
  symboltoken
}) => {

  try {

    if (!smartApi) {

      await createSession({
        apiKey,
        clientId,
        password,
        totp
      });

    }

    const data = await smartApi.marketData({

      mode,

      exchangeTokens: {

        [exchange]: [
          String(symboltoken)
        ]

      }

    });

    return {
      success: true,
      data
    };

  } catch (error) {

    return {
      success: false,
      message: error.message
    };

  }

};

module.exports = {
  createSession,
  connectAngelBroker,
  placeOrder,
  getProfileData,
  getPositions,
  getOrderBook,
  getCandleData,
  getLTPData,
  getMarketData
};
