const httpStatus = require('http-status');
const catchAsync = require('../utils/catchAsync');
const { importService } = require('../services');

const uploadFile = catchAsync(async (req, res) => {
    const result = await importService.uploadFile(req.body);
    res.status(httpStatus.CREATED).send(result);
});

module.exports = {
    uploadFile,
};
