import functools

from aioetcd3.base import StubMixin
from aioetcd3.rpc import rpc_pb2 as rpc
from aioetcd3.rpc import auth_pb2 as auth
from aioetcd3.utils import put_key_range


def call_grpc(request, response_func, method):

    def _f(f):
        @functools.wraps(f)
        async def call(self, *args, timeout=None, **kwargs):
            r = await self.grpc_call(method(self), request(*args, **kwargs), timeout=timeout)
            return response_func(r)

        return call

    return _f


class Auth(StubMixin):
    def _update_channel(self, channel):
        super()._update_channel(channel)
        self._auth_stub = rpc.AuthStub(channel)

    @call_grpc(lambda: rpc.AuthEnableRequest(), lambda r: None, lambda s: s._auth_stub.AuthEnable)
    async def auth_enable(self):
        pass

    @call_grpc(lambda: rpc.AuthDisableRequest(), lambda r: None, lambda s: s._auth_stub.AuthDisable)
    async def auth_disable(self):
        pass

    @call_grpc(lambda u, p: rpc.AuthenticateRequest(name=u, password=p), lambda r: r.token,
               lambda s: s._auth_stub.Authenticate)
    async def authenticate(self, username, password):
        pass

    @call_grpc(lambda: rpc.AuthUserListRequest(), lambda r: [u for u in r.users], lambda s: s._auth_stub.UserList)
    async def user_list(self):
        pass

    @call_grpc(lambda u: rpc.AuthUserGetRequest(name=u), lambda r: [r for r in r.roles],
               lambda s: s._auth_stub.UserGet)
    async def user_get(self, username):
        pass

    @call_grpc(lambda u, p: rpc.AuthUserAddRequest(name=u, password=p), lambda r: None,
               lambda s: s._auth_stub.UserAdd)
    async def user_add(self, username, password):
        pass

    @call_grpc(lambda u: rpc.AuthUserDeleteRequest(name=u), lambda r: None, lambda s: s._auth_stub.UserDelete)
    async def user_delete(self, username):
        pass

    @call_grpc(lambda u, p: rpc.AuthUserChangePasswordRequest(name=u, password=p), lambda r: None,
               lambda s: s._auth_stub.UserChangePassword)
    async def user_change_password(self, username, password):
        pass

    @call_grpc(lambda u, r: rpc.AuthUserGrantRoleRequest(name=u, role=r), lambda r: None,
               lambda s: s._auth_stub.UserGrantRole)
    async def user_grant_role(self, username, role):
        pass

    @call_grpc(lambda u, r: rpc.AuthUserRevokeRoleRequest(name=u, role=r), lambda r: None,
               lambda s: s._auth_stub.UserRevokeRole)
    async def user_revoke_role(self, username, role):
        pass

    @call_grpc(lambda: rpc.AuthRoleListRequest(), lambda r: [role for role in r.roles],
               lambda s: s._auth_stub.RoleList)
    async def role_list(self):
        pass

    @call_grpc(lambda role: rpc.AuthRoleGetRequest(role=role), lambda r: [p for p in r.perm],
               lambda s: s._auth_stub.RoleGet)
    async def role_get(self, name):
        pass

    @call_grpc(lambda role: rpc.AuthRoleAddRequest(name=role), lambda r: None, lambda s: s._auth_stub.RoleAdd)
    async def role_add(self, name):
        pass

    @call_grpc(lambda role: rpc.AuthRoleDeleteRequest(name=role), lambda r: None, lambda s: s._auth_stub.RoleDelete)
    async def role_delete(self, name):
        pass

    @staticmethod
    def role_grant_request(name, key_range, permission):
        if permission not in [auth.Permission.READ, auth.Permission.WRITE, auth.Permission.READWRITE]:
            raise ValueError("permission must be read, write or readwrite")
        per = auth.Permission(permType=permission)
        put_key_range(per, key_range)

        request = rpc.AuthRoleGrantPermissionRequest(name=name, perm=per)

        return request

    @call_grpc(role_grant_request, lambda r: None, lambda s: s._auth_stub.RoleGrantPermission)
    async def role_grant_permission(self, name, key_range, permission):
        pass

    @staticmethod
    def role_revoke_request(role, key_range):
        request = rpc.AuthUserRevokeRoleRequest(name=role)
        put_key_range(request, key_range)

        return request

    @call_grpc(role_revoke_request, lambda r: None, lambda s: s._auth_stub.RoleRevokePermission)
    async def role_revoke_permission(self, name, key_range):
        pass