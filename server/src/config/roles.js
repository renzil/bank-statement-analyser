const allRoles = {
  user: ['uploadRequest'],
  admin: ['getUsers', 'manageUsers', 'uploadRequest'],
};

const roles = Object.keys(allRoles);
const roleRights = new Map(Object.entries(allRoles));

module.exports = {
  roles,
  roleRights,
};
