const Joi = require('joi');

const googleOauthCallback = {
  body: Joi.object().unknown(),
};

const login = {
  body: Joi.object().keys({
    email: Joi.string().required(),
    password: Joi.string().required(),
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
  login,
  logout,
  refreshTokens,
};
