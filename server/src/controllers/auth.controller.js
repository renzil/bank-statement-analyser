const httpStatus = require('http-status');
const catchAsync = require('../utils/catchAsync');
const { userService, tokenService } = require('../services');

const User = require('../models/user.model');
const { OAuth2Client } = require('google-auth-library');
const config = require('../config/config');
const googleOauthClient = new OAuth2Client(config.google.oauth_client_id);

const googleOauthCallback = catchAsync(async (req, res) => {
  const ticket = await googleOauthClient.verifyIdToken({
      idToken: req.body.credential,
      audience: config.google.oauth_client_id,
  });
  const payload = ticket.getPayload();
  const googleUserId = payload['sub'];
  // If request specified a G Suite domain:
  // const domain = payload['hd'];
  const user = await User.findOne({googleUserId: googleUserId});
  if (!user) {
    const newUser = {
      googleUserId,
      name: payload['name'],
      picture: payload['picture'],
      email: payload['email'],
    };
    user = await userService.createUser(newUser);
  }  
  const tokens = await tokenService.generateAuthTokens(user);
  res.status(httpStatus.CREATED).send({ user, tokens });
});

const login = catchAsync(async (req, res) => {
  const { email, password } = req.body;
  const user = await authService.loginUserWithEmailAndPassword(email, password);
  const tokens = await tokenService.generateAuthTokens(user);
  res.send({ user, tokens });
});

const logout = catchAsync(async (req, res) => {
  await authService.logout(req.body.refreshToken);
  res.status(httpStatus.NO_CONTENT).send();
});

const refreshTokens = catchAsync(async (req, res) => {
  const tokens = await authService.refreshAuth(req.body.refreshToken);
  res.send({ ...tokens });
});

module.exports = {
  googleOauthCallback,
  login,
  logout,
  refreshTokens,
};
