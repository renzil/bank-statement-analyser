const Joi = require('joi');

const uploadRequest = {
  body: Joi.object().unknown(),
};

module.exports = {
  uploadRequest,
};
