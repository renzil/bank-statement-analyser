const express = require('express');
const auth = require('../../middlewares/auth');
const validate = require('../../middlewares/validate');
const importValidation = require('../../validations/import.validation');
const importController = require('../../controllers/import.controller');

const router = express.Router();

router
  .route('/upload')
  .post(auth('uploadFile'), validate(importValidation.uploadFile), importController.uploadFile)

module.exports = router;
