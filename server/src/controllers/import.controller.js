const httpStatus = require('http-status');
const catchAsync = require('../utils/catchAsync');
const { importService } = require('../services');

const uploadRequest = catchAsync(async (req, res) => {
    const result = await importService.uploadRequest(req.body);
    res.status(httpStatus.CREATED).send(result);
});

module.exports = {
    uploadRequest,
};
