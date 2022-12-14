const Joi = require('joi');

const uploadFile = {
  body: Joi.object().unknown(),
};

module.exports = {
  uploadFile,
};
