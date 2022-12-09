const Joi = require('joi');

const googleOauthCallback = {
  body: Joi.object().unknown(),
};

const googleLogin = {
  body: Joi.object().keys({
      credential: Joi.string().required()
    }),
};

const logout = {
  body: Joi.object().keys({
    refreshToken: Joi.string().required(),
  }),
};

const refreshTokens = {
  body: Joi.object().keys({
    refreshToken: Joi.string().required(),
  }),
};

module.exports = {
  googleOauthCallback,
  googleLogin,
  logout,
  refreshTokens,
};
